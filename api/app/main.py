import os, hmac, hashlib, json, time, asyncio
from typing import Optional, Dict, Any, List, Tuple

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------
# Storage: Redis with memory fallback (never crash)
# ---------------------------
USE_MEMORY_ONLY = False
_mem_kv: Dict[str, str] = {}
_mem_list: List[str] = []


def _mem_get(key: str) -> Optional[str]:
    return _mem_kv.get(key)


def _mem_set(key: str, val: str):
    _mem_kv[key] = val


def _mem_lpush(key: str, val: str):
    _mem_list.insert(0, val)


def _mem_hset(name: str, key: str, val: str):
    _mem_kv[f"{name}:{key}"] = val


def _mem_hgetall(name: str) -> Dict[str, str]:
    prefix = f"{name}:"
    return {k[len(prefix):]: v for k, v in _mem_kv.items() if k.startswith(prefix)}


REDIS_URL = os.getenv("REDIS_URL", "").strip()
redis_client = None
if REDIS_URL:
    try:
        import redis  # type: ignore

        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        USE_MEMORY_ONLY = True
else:
    USE_MEMORY_ONLY = True


def _get(key: str) -> Optional[str]:
    if USE_MEMORY_ONLY or not redis_client:
        return _mem_get(key)
    try:
        return redis_client.get(key)  # type: ignore[attr-defined]
    except Exception:
        return _mem_get(key)


def _set(key: str, val: str):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_set(key, val)
        return
    try:
        redis_client.set(key, val)  # type: ignore[attr-defined]
    except Exception:
        _mem_set(key, val)


def _lpush(key: str, val: str):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_lpush(key, val)
        return
    try:
        redis_client.lpush(key, val)  # type: ignore[attr-defined]
    except Exception:
        _mem_lpush(key, val)


def _hset(name: str, key: str, val: str):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_hset(name, key, val)
        return
    try:
        redis_client.hset(name, key, val)  # type: ignore[attr-defined]
    except Exception:
        _mem_hset(name, key, val)


def _hgetall(name: str) -> Dict[str, str]:
    if USE_MEMORY_ONLY or not redis_client:
        return _mem_hgetall(name)
    try:
        return redis_client.hgetall(name)  # type: ignore[attr-defined]
    except Exception:
        return _mem_hgetall(name)


def now_ts() -> int:
    return int(time.time())


def audit(event: str, payload: Dict[str, Any]):
    entry = {"ts": now_ts(), "event": event, "payload": payload}
    _lpush("scw:audit", json.dumps(entry))


# ---------------------------
# Config / Security
# ---------------------------
HMAC_SECRET = os.getenv("HMAC_SECRET", "")
ENV_NAME = os.getenv("ENV_NAME", "prod")
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "*")

K_ADMIN = "scw:admin_token"
K_BOOTSTRAP_TS = "scw:bootstrap_ts"
K_LAST_ROTATE_TS = "scw:last_rotate_ts"
K_RESET_SECRET = "scw:reset_secret"
K_SERVICE_REG = "scw:services"
K_DEPLOY_LOG = "scw:deploy_log"

DEPLOY_REPORT_TOKEN = os.getenv("DEPLOY_REPORT_TOKEN", "").strip()
MAX_DEPLOY_LOG = 50


def sig(body: bytes) -> str:
    if not HMAC_SECRET:
        return ""
    return hmac.new(HMAC_SECRET.encode(), body, hashlib.sha256).hexdigest()


def require_admin(x_admin_token: Optional[str]):
    stored = _get(K_ADMIN)
    if not stored:
        raise HTTPException(
            status_code=403, detail="Admin token not set. Bootstrap required."
        )
    if not x_admin_token or x_admin_token != stored:
        raise HTTPException(status_code=403, detail="Invalid admin token.")


# ---------------------------
# Models
# ---------------------------
class BootstrapBody(BaseModel):
    admin_token: str = Field(min_length=16)


class RotateBody(BaseModel):
    new_admin_token: str = Field(min_length=16)
    reset_secret: Optional[str] = None


class BrandWebhooks(BaseModel):
    render: List[str] = []
    netlify: List[str] = []
    vercel: List[str] = []


class BrandManifest(BaseModel):
    brand_id: str
    app_name: str
    package_id: Optional[str] = None
    primary_hex: str
    logo_url: str
    domain: str = ""
    env_overrides: Dict[str, str] = {}
    webhooks: BrandWebhooks = BrandWebhooks()  # additive; server env remains source of truth


class ServiceRegistration(BaseModel):
    name: str
    base_url: str
    hmac_required: bool = True


class DeployReport(BaseModel):
    source: str  # e.g. "github-actions"
    workflow: str
    run_id: str
    run_url: str
    commit_sha: str
    branch: str
    status: str  # "success" | "failure" | "cancelled"
    health_code: int
    health_body: Dict[str, Any] = {}
    ts: int


# ---------------------------
# CFP upstream config + cache
# ---------------------------
CFP_UPSTREAM_URL = os.getenv("CFP_UPSTREAM_URL", "").strip()
CFP_UPSTREAM_KEY_HEADER = os.getenv("CFP_UPSTREAM_KEY_HEADER", "").strip()
CFP_UPSTREAM_KEY_VALUE = os.getenv("CFP_UPSTREAM_KEY_VALUE", "").strip()
CFP_CACHE_SECONDS = int(os.getenv("CFP_CACHE_SECONDS", "600"))

# simple in-memory cache keyed by season (or "latest")
_cfp_cache: Dict[str, Any] = {}
_cfp_cache_ts: Dict[str, int] = {}


def _cfp_cache_get(key: str) -> Optional[Any]:
    ts = _cfp_cache_ts.get(key)
    if not ts:
        return None
    if now_ts() - ts > CFP_CACHE_SECONDS:
        return None
    return _cfp_cache.get(key)


def _cfp_cache_set(key: str, value: Any) -> None:
    _cfp_cache[key] = value
    _cfp_cache_ts[key] = now_ts()


# ---------------------------
# App
# ---------------------------
app = FastAPI(
    title="SCW-API",
    version="1.2.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOW_ORIGINS.split(",")] if ALLOW_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- Root + internal health/status --------
@app.get("/")
def root():
    """
    Simple root endpoint so hitting https://scw-api.onrender.com
    shows a friendly message instead of 404.
    """
    return {
        "ok": True,
        "service": "SCW-API",
        "env": ENV_NAME,
        "health_url": "/v1/ops/health",
        "status_url": "/v1/ops/config/status",
        "external_health_url": "/healthz",
        "cfp_api_url": "/api/cfp",
    }


@app.get("/v1/ops/health")
def health():
    return {
        "ok": True,
        "env": ENV_NAME,
        "admin_set": bool(_get(K_ADMIN)),
        "storage": "memory" if (USE_MEMORY_ONLY or not REDIS_URL) else "redis",
        "redis_url_set": bool(REDIS_URL),
    }


@app.get("/v1/ops/config/status")
def status():
    return {
        "admin_set": bool(_get(K_ADMIN)),
        "bootstrapped_at": _get(K_BOOTSTRAP_TS),
        "last_rotate_at": _get(K_LAST_ROTATE_TS),
        "storage": "memory" if (USE_MEMORY_ONLY or not REDIS_URL) else "redis",
    }


@app.get("/v1/ops/env/required")
def env_required():
    # Show presence (not values) of critical env vars for quick diagnosis
    keys = ["ENV_NAME", "ALLOW_ORIGINS", "HMAC_SECRET", "DEPLOY_REPORT_TOKEN", "REDIS_URL"]
    present = {k: bool(os.getenv(k)) for k in keys}
    return {"ok": True, "present": present}


@app.post("/v1/ops/config/bootstrap")
def bootstrap(body: BootstrapBody):
    if _get(K_ADMIN):
        raise HTTPException(status_code=409, detail="Admin token already set. Use rotate.")
    _set(K_ADMIN, body.admin_token)
    _set(K_BOOTSTRAP_TS, str(now_ts()))
    audit("bootstrap", {"ok": True})
    return {"ok": True, "message": "Admin token set."}


@app.post("/v1/ops/config/rotate")
def rotate(
    body: RotateBody,
    x_admin_token: Optional[str] = Header(None, convert_underscores=False),
):
    stored = _get(K_ADMIN)
    if not stored:
        raise HTTPException(status_code=403, detail="Admin token not set. Bootstrap required.")
    reset_secret = _get(K_RESET_SECRET)
    if x_admin_token != stored and (not reset_secret or body.reset_secret != reset_secret):
        raise HTTPException(status_code=403, detail="Invalid admin token or reset secret.")
    _set(K_ADMIN, body.new_admin_token)
    _set(K_LAST_ROTATE_TS, str(now_ts()))
    audit("rotate", {"ok": True})
    return {"ok": True, "message": "Admin token rotated."}


@app.post("/v1/ops/service/register")
def svc_register(
    body: ServiceRegistration,
    x_admin_token: Optional[str] = Header(None, convert_underscores=False),
):
    require_admin(x_admin_token)
    _hset(K_SERVICE_REG, body.name, json.dumps(body.dict()))
    audit("service_register", {"name": body.name})
    return {"ok": True, "message": "Service registered."}


# ---------------------------
# Build trigger (fan-out via env webhooks)
# ---------------------------
class HookResult(BaseModel):
    url: str
    status: int
    body: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.post("/v1/ops/build/trigger")
def build_trigger(
    manifest: BrandManifest,
    x_admin_token: Optional[str] = Header(None, convert_underscores=False),
):
    require_admin(x_admin_token)
    render_hooks = [h for h in os.getenv("RENDER_HOOKS", "").split(",") if h.strip()]
    netlify_hooks = [h for h in os.getenv("NETLIFY_HOOKS", "").split(",") if h.strip()]
    vercel_hooks = [h for h in os.getenv("VERCEL_HOOKS", "").split(",") if h.strip()]
    render_hooks += manifest.webhooks.render
    netlify_hooks += manifest.webhooks.netlify
    vercel_hooks += manifest.webhooks.vercel

    payload = {"brand": manifest.dict(), "meta": {"ts": now_ts(), "env": ENV_NAME}}

    async def fire(url: str):
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, json=payload)
                try:
                    body = resp.json()
                except Exception:
                    body = {"text": resp.text[:500]}
                return HookResult(url=url, status=resp.status_code, body=body)
        except Exception as e:
            return HookResult(url=url, status=0, error=str(e)[:400] or "error")

    tasks = [fire(u) for u in (render_hooks + netlify_hooks + vercel_hooks)]
    results = asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks)) if tasks else []
    audit(
        "build_trigger",
        {"brand_id": manifest.brand_id, "results": [r.dict() for r in results]},
    )
    return {"ok": True, "brand_id": manifest.brand_id, "hook_results": [r.dict() for r in results]}


# ---------------------------
# Deploy summary receiver + listing (for Actions to report)
# ---------------------------
@app.post("/v1/ops/deploy/report")
def deploy_report(report: DeployReport, authorization: Optional[str] = Header(None)):
    if not DEPLOY_REPORT_TOKEN:
        raise HTTPException(status_code=503, detail="DEPLOY_REPORT_TOKEN not configured.")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")
    token = authorization.split(" ", 1)[1]
    if token != DEPLOY_REPORT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token.")
    _lpush(K_DEPLOY_LOG, json.dumps(report.dict()))
    try:
        if redis_client:
            redis_client.ltrim(K_DEPLOY_LOG, 0, MAX_DEPLOY_LOG - 1)  # type: ignore[attr-defined]
    except Exception:
        pass
    audit("deploy_report", {"status": report.status, "sha": report.commit_sha})
    return {"ok": True}


@app.get("/v1/ops/deploy/summary")
def deploy_summary(limit: int = 10):
    limit = max(1, min(limit, MAX_DEPLOY_LOG))
    try:
        if redis_client:
            raw = redis_client.lrange(K_DEPLOY_LOG, 0, limit - 1)  # type: ignore[attr-defined]
        else:
            raw = _mem_list[:limit]
    except Exception:
        raw = _mem_list[:limit]
    items: List[Dict[str, Any]] = []
    for line in raw:
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    return {"ok": True, "items": items}


# ---------------------------
# CFP API: /api/cfp
# ---------------------------
@app.get("/api/cfp")
async def get_cfp(season: Optional[int] = None):
    """
    Proxy endpoint used by Site workflows.

    - Reads from CFP_UPSTREAM_URL (required).
    - Passes through ?season=YYYY if provided.
    - Optional auth header via CFP_UPSTREAM_KEY_HEADER / CFP_UPSTREAM_KEY_VALUE.
    - Returns the upstream JSON **as-is**.
    - Uses a small in-memory cache to avoid hammering the provider.
    """
    if not CFP_UPSTREAM_URL:
        raise HTTPException(status_code=503, detail="CFP_UPSTREAM_URL not configured.")

    cache_key = str(season or "latest")
    cached = _cfp_cache_get(cache_key)
    if cached is not None:
        return cached

    params: Dict[str, Any] = {}
    if season is not None:
        params["season"] = season

    headers: Dict[str, str] = {}
    if CFP_UPSTREAM_KEY_HEADER and CFP_UPSTREAM_KEY_VALUE:
        headers[CFP_UPSTREAM_KEY_HEADER] = CFP_UPSTREAM_KEY_VALUE

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(CFP_UPSTREAM_URL, params=params, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error calling CFP upstream: {e}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"CFP upstream returned HTTP {resp.status_code}",
        )

    try:
        data = resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="CFP upstream did not return valid JSON.")

    _cfp_cache_set(cache_key, data)
    return data


@app.get("/api/cfp/status")
def cfp_status():
    """
    Quick diagnostics for the CFP module.
    """
    return {
        "ok": bool(CFP_UPSTREAM_URL),
        "upstream_url_set": bool(CFP_UPSTREAM_URL),
        "cache_seconds": CFP_CACHE_SECONDS,
        "has_cached_keys": list(_cfp_cache_ts.keys()),
    }


# ---------------------------
# External health for monitors (/healthz)
# ---------------------------
@app.get("/healthz")
def external_health():
    """
    Simple, stable health endpoint suitable for uptime monitors.
    Aggregates the internal health + config status into one payload.
    """
    h = health()
    s = status()
    return {
        "ok": h.get("ok", False)
        and bool(s.get("admin_set", False) or s.get("bootstrapped_at") is not None),
        "env": h.get("env"),
        "storage": h.get("storage"),
        "redis_url_set": h.get("redis_url_set"),
        "admin_set": s.get("admin_set"),
        "bootstrapped_at": s.get("bootstrapped_at"),
        "last_rotate_at": s.get("last_rotate_at"),
    }
