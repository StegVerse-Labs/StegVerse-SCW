import os, hmac, hashlib, json, time
from typing import Optional, Dict, Any, List

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

# CFP keys
K_CFP_CURRENT_SEASON = "cfp:current_season"          # optional override
K_CFP_SEASON_PREFIX = "cfp:season:"                  # e.g. "cfp:season:2025"

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


# ----- CFP models -----
class CFPTeam(BaseModel):
    rank: int
    team: str
    record: str
    conf: str
    last_rank: Optional[int] = None
    movement: Optional[int] = None
    projection: Optional[str] = None  # e.g. "hold", "up", "down"


class CFPState(BaseModel):
    season: int
    week: int
    released_at: Optional[str] = None  # ISO timestamp or human string
    note: Optional[str] = None
    rankings: List[CFPTeam] = []


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
        "cfp_url": "/api/cfp",
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


# ---------------------------
# Bootstrap / Rotate Admin
# ---------------------------
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


# ---------------------------
# Service registration
# ---------------------------
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

    import asyncio

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


# =====================================================================
# CFP MODULE
# =====================================================================

def _cfp_season_key(season: int) -> str:
    return f"{K_CFP_SEASON_PREFIX}{season}"


def _get_current_cfp_season() -> int:
    # order of precedence:
    #   1) stored override in storage
    #   2) ENV CFP_SEASON
    #   3) default 2025
    stored = _get(K_CFP_CURRENT_SEASON)
    if stored:
        try:
            return int(stored)
        except ValueError:
            pass
    env_val = os.getenv("CFP_SEASON")
    if env_val:
        try:
            return int(env_val)
        except ValueError:
            pass
    return 2025


def _load_cfp_state(season: int) -> CFPState:
    raw = _get(_cfp_season_key(season))
    if raw:
        try:
            return CFPState.parse_raw(raw)
        except Exception:
            pass

    # Fallback: empty state with a helpful note so callers still get 200/JSON.
    return CFPState(
        season=season,
        week=0,
        released_at=None,
        note="No CFP data stored yet for this season.",
        rankings=[],
    )


def _save_cfp_state(state: CFPState):
    key = _cfp_season_key(state.season)
    _set(key, state.json())
    # if this is the newest season we've seen, record it as current
    current = _get_current_cfp_season()
    if state.season >= current:
        _set(K_CFP_CURRENT_SEASON, str(state.season))


@app.get("/api/cfp")
def cfp_current():
    """
    Return current CFP state for the active season.
    This is what CFP Data Sync / front-end should normally call.
    """
    season = _get_current_cfp_season()
    state = _load_cfp_state(season)
    return {
        "ok": True,
        "season": state.season,
        "week": state.week,
        "released_at": state.released_at,
        "note": state.note,
        "rankings": [t.dict() for t in state.rankings],
    }


@app.get("/api/cfp/{season}")
def cfp_by_season(season: int):
    """
    Fetch CFP state for a specific season (e.g. /api/cfp/2025).
    """
    state = _load_cfp_state(season)
    return {
        "ok": True,
        "season": state.season,
        "week": state.week,
        "released_at": state.released_at,
        "note": state.note,
        "rankings": [t.dict() for t in state.rankings],
    }


@app.post("/api/cfp/{season}")
def cfp_upsert(
    season: int,
    state: CFPState,
    x_admin_token: Optional[str] = Header(None, convert_underscores=False),
):
    """
    Admin-only upsert of CFP state for a season.

    Intended usage:
      - GitHub Actions or admin tools POST new rankings here
      - SCW-API persists them (Redis or in-memory)
      - Site repo sync job pulls via CFP_API_URL and writes JSON files
    """
    require_admin(x_admin_token)
    # Trust path param as the source of truth for season
    state.season = season
    _save_cfp_state(state)
    audit(
        "cfp_upsert",
        {"season": state.season, "week": state.week, "count": len(state.rankings)},
    )
    return {"ok": True, "season": state.season, "saved": len(state.rankings)}


@app.get("/api/cfp/meta")
def cfp_meta():
    """
    Lightweight meta endpoint for diagnostics.
    """
    current = _get_current_cfp_season()
    raw_keys = [k for k in _mem_kv.keys() if k.startswith(K_CFP_SEASON_PREFIX)]
    if redis_client:
        try:
            raw_keys = list(
                set(raw_keys)
                | {
                    k
                    for k in redis_client.scan_iter(f"{K_CFP_SEASON_PREFIX}*")  # type: ignore[attr-defined]
                }
            )
        except Exception:
            pass
    seasons: List[int] = []
    for k in raw_keys:
        try:
            seasons.append(int(k.split(":")[-1]))
        except Exception:
            continue
    seasons = sorted(set(seasons))
    return {
        "ok": True,
        "current_season": current,
        "seasons_with_data": seasons,
    }


# Aliases so older clients using CFP_API_URL + "/cfp" or "/cfp/{season}" still work
@app.get("/cfp")
def cfp_current_alias():
    return cfp_current()


@app.get("/cfp/{season}")
def cfp_by_season_alias(season: int):
    return cfp_by_season(season)
