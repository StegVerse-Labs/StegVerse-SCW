# FULL MAIN.PY GENERATED FOR SCW-API
# VERSION: 2025-11-30
# Includes CFP Module, External Health Suite, Build Trigger, Deploy Logging

import os, hmac, hashlib, json, time, asyncio
from typing import Optional, Dict, Any, List

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================
# STORAGE LAYER (Redis w/ Memory Fallback)
# ============================================================

USE_MEMORY_ONLY = False
_mem_kv: Dict[str, str] = {}
_mem_list: List[str] = []

def _mem_get(key): return _mem_kv.get(key)
def _mem_set(key,val): _mem_kv[key] = val
def _mem_lpush(key,val): _mem_list.insert(0,val)
def _mem_hset(name,key,val): _mem_kv[f"{name}:{key}"] = val
def _mem_hgetall(name):
    p = f"{name}:"
    return {k[len(p):]: v for k,v in _mem_kv.items() if k.startswith(p)}

REDIS_URL = os.getenv("REDIS_URL","").strip()
redis_client = None

if REDIS_URL:
    try:
        import redis
        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except:
        USE_MEMORY_ONLY = True
else:
    USE_MEMORY_ONLY = True

def _get(key):
    if USE_MEMORY_ONLY or not redis_client:
        return _mem_get(key)
    try: return redis_client.get(key)
    except: return _mem_get(key)

def _set(key,val):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_set(key,val); return
    try: redis_client.set(key,val)
    except: _mem_set(key,val)

def _lpush(key,val):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_lpush(key,val); return
    try: redis_client.lpush(key,val)
    except: _mem_lpush(key,val)

def _hset(name,key,val):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_hset(name,key,val); return
    try: redis_client.hset(name,key,val)
    except: _mem_hset(name,key,val)

def _hgetall(name):
    if USE_MEMORY_ONLY or not redis_client:
        return _mem_hgetall(name)
    try: return redis_client.hgetall(name)
    except: return _mem_hgetall(name)

def now_ts(): return int(time.time())

def audit(event: str, payload: Dict[str, Any]):
    _lpush("scw:audit", json.dumps({"ts": now_ts(), "event": event, "payload": payload}))


# ============================================================
# CONFIG / SECURITY
# ============================================================

HMAC_SECRET = os.getenv("HMAC_SECRET","")
ENV_NAME = os.getenv("ENV_NAME","prod")
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS","*")

K_ADMIN="scw:admin_token"
K_BOOT="scw:bootstrap_ts"
K_ROTATE="scw:last_rotate_ts"
K_RESET="scw:reset_secret"
K_SERVICES="scw:services"
K_DEPLOY="scw:deploy_log"

DEPLOY_REPORT_TOKEN = os.getenv("DEPLOY_REPORT_TOKEN","").strip()
MAX_DEPLOY_LOG = 50

def require_admin(tok):
    stored = _get(K_ADMIN)
    if not stored:
        raise HTTPException(403,"Admin token not set. Bootstrap required.")
    if not tok or tok != stored:
        raise HTTPException(403,"Invalid admin token")


# ============================================================
# MODELS
# ============================================================

class BootstrapBody(BaseModel):
    admin_token: str = Field(min_length=16)

class RotateBody(BaseModel):
    new_admin_token: str = Field(min_length=16)
    reset_secret: Optional[str] = None

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
    health_body: Dict[str,Any] = {}
    ts: int

class ExternalHealthResult(BaseModel):
    name: str
    url: str
    status: int
    ok: bool
    body: Optional[Dict[str,Any]] = None
    error: Optional[str] = None


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="SCW-API",
    version="1.2.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOW_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ROOT / BASIC HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "ok": True,
        "service": "SCW-API",
        "env": ENV_NAME,
        "health": "/v1/ops/health",
        "config": "/v1/ops/config/status",
        "external_health": "/healthz"
    }

@app.get("/v1/ops/health")
def health():
    return {
        "ok": True,
        "env": ENV_NAME,
        "admin_set": bool(_get(K_ADMIN)),
        "storage": "memory" if USE_MEMORY_ONLY or not REDIS_URL else "redis",
        "redis_url_set": bool(REDIS_URL)
    }

@app.get("/v1/ops/config/status")
def config_status():
    return {
        "admin_set": bool(_get(K_ADMIN)),
        "bootstrapped_at": _get(K_BOOT),
        "last_rotate_at": _get(K_ROTATE),
        "storage": "memory" if USE_MEMORY_ONLY or not REDIS_URL else "redis",
    }

@app.get("/healthz")
def external_health():
    h=health()
    s=config_status()
    return {
        "ok": h["ok"] and s["admin_set"],
        "env": ENV_NAME,
        "admin_set": s["admin_set"],
        "bootstrapped_at": s["bootstrapped_at"]
    }


# ============================================================
# SERVICE REGISTRATION + EXTERNAL HEALTH CHECK
# ============================================================

async def _check_service(name, base_url):
    base = base_url.rstrip("/")
    candidates = [f"{base}/v1/ops/health", f"{base}/health"]

    last_err = "failed"
    for url in candidates:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(url)
            try: body = r.json()
            except: body = {"raw": r.text[:500]}

            return ExternalHealthResult(
                name=name,
                url=url,
                status=r.status_code,
                ok=(r.status_code<500 and body.get("ok",True)),
                body=body
            )
        except Exception as e:
            last_err = str(e)

    return ExternalHealthResult(
        name=name,
        url=candidates[-1],
        status=0,
        ok=False,
        body=None,
        error=last_err
    )

@app.get("/v1/ops/health/full")
def full_health():
    internal = health()
    raw = _hgetall(K_SERVICES)

    services = []
    for name,val in raw.items():
        try:
            svc = json.loads(val)
            svc["name"]=name
            services.append(svc)
        except:
            continue

    results = []
    if services:
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            asyncio.gather(*[
                _check_service(s["name"], s["base_url"])
                for s in services
            ])
        )

    overall_ok = internal["ok"] and all(r.ok for r in results)
    payload = {
        "ok": overall_ok,
        "internal": internal,
        "external": [r.dict() for r in results]
    }
    audit("external_health", payload)
    return payload


@app.post("/v1/ops/service/register")
def svc_register(body: ServiceRegistration,
                 x_admin_token: Optional[str]=Header(None, convert_underscores=False)):
    require_admin(x_admin_token)
    _hset(K_SERVICES, body.name, json.dumps(body.dict()))
    audit("service_register", {"name": body.name})
    return {"ok": True}


# ============================================================
# CFP MODULE — SIMPLE JSON ENDPOINTS
# ============================================================

CFP_DATA_PATH = "/app/cfp-data"   # Render container path
os.makedirs(CFP_DATA_PATH, exist_ok=True)

def _read_json(name):
    path = f"{CFP_DATA_PATH}/{name}.json"
    if not os.path.exists(path):
        return {}
    try:
        return json.load(open(path))
    except:
        return {}

@app.get("/api/cfp/teams")
def cfp_teams():
    return _read_json("cfp-teams")

@app.get("/api/cfp/data")
def cfp_data():
    return _read_json("cfp-data")

@app.get("/api/cfp/tickets")
def cfp_tickets():
    return _read_json("cfp-tickets")


# ============================================================
# DEPLOY REPORT RECEIVER
# ============================================================

@app.post("/v1/ops/deploy/report")
def deploy_report(report: DeployReport, authorization: Optional[str]=Header(None)):
    if not DEPLOY_REPORT_TOKEN:
        raise HTTPException(503,"DEPLOY_REPORT_TOKEN not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401,"Missing bearer token")

    token = authorization.split(" ",1)[1]
    if token != DEPLOY_REPORT_TOKEN:
        raise HTTPException(403,"Invalid token")

    _lpush(K_DEPLOY, json.dumps(report.dict()))

    try:
        if redis_client:
            redis_client.ltrim(K_DEPLOY,0,MAX_DEPLOY_LOG-1)
    except:
        pass

    audit("deploy_report", {"sha":report.commit_sha})
    return {"ok": True}

@app.get("/v1/ops/deploy/summary")
def deploy_summary(limit: int=10):
    limit = max(1,min(limit,MAX_DEPLOY_LOG))
    try:
        raw = redis_client.lrange(K_DEPLOY,0,limit-1) if redis_client else _mem_list[:limit]
    except:
        raw = _mem_list[:limit]

    items=[]
    for line in raw:
        try: items.append(json.loads(line))
        except: pass

    return {"ok": True, "items": items}
