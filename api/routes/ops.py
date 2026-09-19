# ruff: noqa: E401,E501,I001
# api/routes/ops.py
import os, json, time, urllib.request, urllib.error, secrets
from hmac import compare_digest
from typing import Optional, Dict, Any

import redis
from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/v1/ops", tags=["ops"])

# -----------------------------
# Redis & config helpers
# -----------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_cfg(name: str, default: Optional[str] = None) -> Optional[str]:
    v = r.get(f"config:{name}")
    if v is not None:
        return v
    return os.getenv(name, default)

def set_cfg(name: str, value: Optional[str]):
    key = f"config:{name}"
    if value is None or value == "":
        r.delete(key)
    else:
        r.set(key, value)

def cfg_dict(*names: str) -> Dict[str, Optional[str]]:
    return {n: get_cfg(n) for n in names}

# All known config keys (add here if you introduce new ones)
CFG_KEYS = [
    "ADMIN_TOKEN",
    "SCW_UI_URL",
    "SCW_API_URL",
    "MIN_REDEPLOY_INTERVAL_S",
]

def _admin_token() -> str:
    return get_cfg("ADMIN_TOKEN", "") or ""

def _auth(token: Optional[str]):
    admin = _admin_token()
    if not admin:
        raise HTTPException(status_code=501, detail="admin ops not configured")
    if not token or token != admin:
        raise HTTPException(status_code=403, detail="forbidden")

_last_call_at: Dict[str, float] = {}
def _throttle(key: str):
    now = time.time()
    last = _last_call_at.get(key, 0)
    gap = int(get_cfg("MIN_REDEPLOY_INTERVAL_S", "15") or "15")
    if now - last < gap:
        raise HTTPException(status_code=429, detail=f"too many requests; retry after {int(gap - (now - last))}s")
    _last_call_at[key] = now

def _post_json(url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
    req = urllib.request.Request(url, method="POST")
    if headers:
        for k, v in (headers or {}).items():
            req.add_header(k, v)
    if data is None:
        data = {}
    body = json.dumps(data).encode("utf-8")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, body, timeout=30) as r_:
        return r_.status, r_.read().decode("utf-8", "ignore")

# -----------------------------
# NEW: locks, token gen, recovery
# -----------------------------
# One-time out-of-band recovery code (set in env of API service)
RECOVERY_CODE = os.getenv("ADMIN_RECOVERY_CODE", "")

def _gen_token(nbytes: int = 48) -> str:
    # urlsafe, long enough to pass >10 chars check
    return secrets.token_urlsafe(nbytes)

LOCK_PREFIX = "lock:"
def _acquire_lock(name: str, ttl: int = 60) -> tuple[bool, str]:
    token = secrets.token_hex(16)
    ok = r.set(f"{LOCK_PREFIX}{name}", token, nx=True, ex=ttl)
    return bool(ok), token

def _release_lock(name: str, token: str):
    k = f"{LOCK_PREFIX}{name}"
    v = r.get(k)
    if v == token:
        r.delete(k)

# -----------------------------
# Bootstrap (first run)
# -----------------------------
@router.post("/config/bootstrap")
def config_bootstrap(payload: Dict[str, str]):
    """
    First-time setup ONLY:
    - If ADMIN_TOKEN is not configured (Redis/env), allow setting it once.
    """
    if _admin_token():
        raise HTTPException(status_code=409, detail="admin already configured")
    token = (payload or {}).get("ADMIN_TOKEN", "").strip()
    if not token or len(token) < 10:
        raise HTTPException(status_code=400, detail="weak or missing ADMIN_TOKEN")
    set_cfg("ADMIN_TOKEN", token)
    return {"ok": True, "message": "admin token set"}

@router.get("/config/bootstrap/status")
def config_bootstrap_status():
    return {"bootstrap_open": not bool(_admin_token())}

# -----------------------------
# Read-only snapshot (no auth)
# -----------------------------
@router.get("/snapshot")
def snapshot():
    ui = (get_cfg("SCW_UI_URL", "") or "").rstrip("/")
    api = (get_cfg("SCW_API_URL", "") or "").rstrip("/")

    def jget(u):
        try:
            with urllib.request.urlopen(u, timeout=12) as r_:
                return True, json.loads(r_.read().decode("utf-8", "ignore"))
        except Exception as e:
            return False, str(e)

    ok_api, who = jget(api + "/whoami")
    ok_rep, rep = jget(api + "/v1/legal/report/latest")
    ok_alerts, alerts = jget(api + "/v1/legal/alerts")
    missing = [k for k in CFG_KEYS if not get_cfg(k)]
    return {
        "ui": {"base": ui},
        "api": {"base": api, "ok": ok_api, "whoami": who},
        "report": {"ok": ok_rep},
        "alerts": {"ok": ok_alerts},
        "config_missing": missing,
    }

# -----------------------------
# Config management (auth)
# -----------------------------
@router.get("/config/list")
def config_list(x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")):
    _auth(x_admin_token)
    out = {}
    for k in CFG_KEYS:
        v = get_cfg(k)
        out[k] = ("<set>" if v else None)
    return {"ok": True, "keys": out}

@router.get("/config/get/{name}")
def config_get(name: str, x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")):
    _auth(x_admin_token)
    if name not in CFG_KEYS:
        raise HTTPException(status_code=400, detail="unknown key")
    return {"ok": True, "name": name, "value": get_cfg(name)}

@router.post("/config/set")
def config_set(payload: Dict[str, str], x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")):
    _auth(x_admin_token)
    changed = {}
    for k, v in (payload or {}).items():
        if k not in CFG_KEYS:
            continue
        set_cfg(k, v)
        changed[k] = "<set>" if v else None
    return {"ok": True, "changed": changed}

# -----------------------------
# Mutating ops (auth)
# -----------------------------
# Worker reset (Redis keys)
@router.post("/worker/reset")
def worker_reset(payload: Dict[str, Any] | None = None, x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")):
    """
    Safely reset worker state in Redis.
    - dry_run (bool): report-only
    - purge_runs (bool): delete run queues + per-run logs/results
    """
    _auth(x_admin_token)
    dry = bool((payload or {}).get("dry_run", False))
    purge_runs = bool((payload or {}).get("purge_runs", True))

    summary = {"deleted": [], "kept": [], "notes": []}

    queue_keys = ["runs"]
    run_keys = []
    if purge_runs:
        cursor = 0
        while True:
            cursor, batch = r.scan(cursor=cursor, match="run:*", count=500)
            run_keys.extend(batch)
            if cursor == 0:
                break

    targets = []
    for k in queue_keys:
        if r.exists(k):
            targets.append(k)
    targets.extend(run_keys)

    summary["notes"].append(f"found {len(targets)} keys to remove")

    if dry:
        summary["deleted"] = targets
        return {"ok": True, "dry_run": True, "summary": summary}

    deleted = 0
    for k in targets:
        try:
            r.delete(k)
            deleted += 1
            summary["deleted"].append(k)
        except Exception as e:
            summary["kept"].append({"key": k, "error": str(e)})

    summary["notes"].append(f"deleted {deleted} keys")
    return {"ok": True, "dry_run": False, "summary": summary}

# -----------------------------
# NEW: token rotation + recovery + one-click reset
# -----------------------------
@router.post("/admin/rotate_token")
def admin_rotate_token(x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")):
    _auth(x_admin_token)
    new_tok = _gen_token()
    set_cfg("ADMIN_TOKEN", new_tok)
    return {"ok": True, "new_admin_token": new_tok}

@router.post("/admin/recover")
def admin_recover(payload: Dict[str, str] | None = None):
    """
    Recovery path if ADMIN_TOKEN is lost.
    Requires ADMIN_RECOVERY_CODE (env) to match payload.recovery_code.
    """
    if not RECOVERY_CODE:
        raise HTTPException(status_code=501, detail="recovery not configured")
    code = (payload or {}).get("recovery_code", "").strip()
    if not code or not compare_digest(code, RECOVERY_CODE):
        raise HTTPException(status_code=403, detail="invalid recovery code")

    new_tok = _gen_token()
    set_cfg("ADMIN_TOKEN", new_tok)
    return {"ok": True, "new_admin_token": new_tok}
