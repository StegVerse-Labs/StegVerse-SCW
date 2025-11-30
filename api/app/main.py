import os, hmac, hashlib, json, time, asyncio
from typing import Optional, Dict, Any, List

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# =============================================================================
# Storage: Redis with memory fallback
# =============================================================================
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
        import redis
        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        USE_MEMORY_ONLY = True
else:
    USE_MEMORY_ONLY = True


def _get(key: str) -> Optional[str]:
    if USE_MEMORY_ONLY or not redis_client:
        return _mem_get(key)
    try:
        return redis_client.get(key)
    except Exception:
        return _mem_get(key)


def _set(key: str, val: str):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_set(key, val)
        return
    try:
        redis_client.set(key, val)
    except Exception:
        _mem_set(key, val)


def _lpush(key: str, val: str):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_lpush(key, val)
        return
    try:
        redis_client.lpush(key, val)
    except Exception:
        _mem_lpush(key, val)


def _hset(name: str, key: str, val: str):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_hset(name, key, val)
        return
    try:
        redis_client.hset(name, key, val)
    except Exception:
        _mem_hset(name, key, val)


def _hgetall(name: str) -> Dict[str, str]:
    if USE_MEMORY_ONLY or not redis_client:
        return _mem_hgetall(name)
    try:
        return redis_client.hgetall(name)
    except Exception:
        return _mem_hgetall(name)


def now_ts() -> int:
    return int(time.time())


def audit(event: str, payload: Dict[str, Any]):
    entry = {"ts": now_ts(), "event": event, "payload": payload}
    _lpush("scw:audit", json.dumps(entry))


# =============================================================================
# Config / Security
# =============================================================================
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


# =============================================================================
# HMAC
# =============================================================================
def sig(body: bytes) -> str:
    if not HMAC_SECRET:
        return ""
    return hmac.new(HMAC_SECRET.encode(), body, hashlib.sha256).hexdigest()


def require_admin(x_admin_token: Optional[str]):
    stored = _get(K_ADMIN)
    if not stored:
        raise HTTPException(status_code=403, detail="Admin token not set. Bootstrap required.")
    if not x_admin_token or x_admin_token != stored:
        raise HTTPException(status_code=403, detail="Invalid admin token.")


# =============================================================================
# Models (Admin + Config)
# =============================================================================
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
    webhooks: BrandWebhooks = BrandWebhooks()


class ServiceRegistration(BaseModel):
    name: str
    base_url: str
    hmac_required: bool = True


class DeployReport(BaseModel):
    source: str
    workflow: str
    run_id: str
    run_url: str
    commit_sha: str
    branch: str
    status: str
    health_code: int
    health_body: Dict[str, Any] = {}
    ts: int


# =============================================================================
# CFP Module Models
# =============================================================================
class CFPTeam(BaseModel):
    id: str
    name: str
    conference: str
    ranking: int


class CFPData(BaseModel):
    year: int
    teams: List[CFPTeam]


# =============================================================================
# FastAPI App
# =============================================================================
app = FastAPI(
    title="SCW-API",
    version="1.2.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOW_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Root + Internal Health
# =============================================================================
@app.get("/")
def root():
    return {
        "ok": True,
        "service": "SCW-API",
        "env": ENV_NAME,
        "healthz": "/healthz",
    }


@app.get("/healthz")
def external_health():
    """Render health check endpoint."""
    status = bool(_get(K_ADMIN)) or bool(_get(K_BOOTSTRAP_TS))
    return {
        "ok": status,
        "env": ENV_NAME,
        "admin_set": bool(_get(K_ADMIN)),
    }


@app.get("/v1/ops/health")
def internal_health():
    return {
        "ok": True,
        "env": ENV_NAME,
        "admin_set": bool(_get(K_ADMIN)),
        "storage": "memory" if (USE_MEMORY_ONLY or not REDIS_URL) else "redis",
        "redis_url_set": bool(REDIS_URL),
    }


@app.get("/v1/ops/config/status")
def config_status():
    return {
        "admin_set": bool(_get(K_ADMIN)),
        "bootstrapped_at": _get(K_BOOTSTRAP_TS),
        "last_rotate_at": _get(K_LAST_ROTATE_TS),
        "storage": "memory" if (USE_MEMORY_ONLY or not REDIS_URL) else "redis",
    }


# =============================================================================
# Admin Ops
# =============================================================================
@app.post("/v1/ops/config/bootstrap")
def bootstrap(body: BootstrapBody):
    if _get(K_ADMIN):
        raise HTTPException(status_code=409, detail="Admin token already set. Use rotate.")
    _set(K_ADMIN, body.admin_token)
    _set(K_BOOTSTRAP_TS, str(now_ts()))
    audit("bootstrap", {"ok": True})
    return {"ok": True}


@app.post("/v1/ops/config/rotate")
def rotate(body: RotateBody, x_admin_token: Optional[str] = Header(None, convert_underscores=False)):
    stored = _get(K_ADMIN)
    if not stored:
        raise HTTPException(status_code=403, detail="Admin token not set.")
    reset_secret = _get(K_RESET_SECRET)
    if x_admin_token != stored and (not reset_secret or reset_secret != body.reset_secret):
        raise HTTPException(status_code=403, detail="Invalid admin token.")
    _set(K_ADMIN, body.new_admin_token)
    _set(K_LAST_ROTATE_TS, str(now_ts()))
    audit("rotate", {"ok": True})
    return {"ok": True}


# =============================================================================
# CFP API MODULE
# =============================================================================

CFP_STORE_KEY = "scw:cfp_data"   # stored JSON blob in Redis/memory


@app.get("/v1/cfp/ping")
def cfp_ping():
    return {"ok": True, "module": "cfp"}


@app.get("/v1/cfp/current")
def cfp_current():
    raw = _get(CFP_STORE_KEY)
    if not raw:
        raise HTTPException(status_code=404, detail="No CFP data stored yet.")
    try:
        return json.loads(raw)
    except:
        raise HTTPException(status_code=500, detail="Stored CFP data corrupted.")


@app.post("/v1/cfp/update")
def cfp_update(
    data: CFPData,
    x_admin_token: Optional[str] = Header(None, convert_underscores=False),
):
    require_admin(x_admin_token)
    payload = data.dict()
    _set(CFP_STORE_KEY, json.dumps(payload))
    audit("cfp_update", {"year": data.year, "teams": len(data.teams)})
    return {"ok": True, "stored_year": data.year}


# =============================================================================
# Build + Deploy Handlers (unchanged)
# =============================================================================
class HookResult(BaseModel):
    url: str
    status: int
    body: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.post("/v1/ops/deploy/report")
def deploy_report(report: DeployReport, authorization: Optional[str] = Header(None)):
    if not DEPLOY_REPORT_TOKEN:
        raise HTTPException(status_code=503, detail="DEPLOY_REPORT_TOKEN missing")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    if token != DEPLOY_REPORT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    _lpush(K_DEPLOY_LOG, json.dumps(report.dict()))
    audit("deploy_report", {"sha": report.commit_sha})
    return {"ok": True}


@app.get("/v1/ops/deploy/summary")
def deploy_summary(limit: int = 10):
    limit = max(1, min(limit, MAX_DEPLOY_LOG))
    raw = _mem_list[:limit]
    items = []
    for line in raw:
        try:
            items.append(json.loads(line))
        except:
            pass
    return {"ok": True, "items": items}
