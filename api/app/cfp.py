import os, json, time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
import httpx

# -----------------------------------------------------
# CFP MODULE (SCW-API)
# Purpose:
#   - Provide stable JSON endpoints for:
#         /api/cfp/teams
#         /api/cfp/data
#         /api/cfp/tickets
#         /api/cfp/raw
#
#   - Pulls CFP + NCAAF data from official sources
#   - Normalizes & caches in Redis/memory
#   - Exposed for GitHub Actions auto-sync
# -----------------------------------------------------

router = APIRouter(prefix="/api/cfp", tags=["CFP"])

CFP_CACHE_KEY = "cfp:latest"
CACHE_TTL = 3600     # 1 hour

CFP_SOURCE_TEAMS = "https://site.api.ncaa.com/contest/football/fbs/teams.json"
CFP_SOURCE_NCAA   = "https://site.api.ncaa.com/contest/football/fbs/scoreboard.json"
CFP_SOURCE_TICKETS = "https://api.stubhub.com/catalog/events/v3/football-college"

# Same storage helpers as main app ---------------------
USE_MEMORY_ONLY = False
_mem_kv: Dict[str, str] = {}

def _mem_get(k): return _mem_kv.get(k)
def _mem_set(k, v): _mem_kv[k] = v

REDIS_URL = os.getenv("REDIS_URL", "")
redis_client = None
if REDIS_URL:
    try:
        import redis
        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        USE_MEMORY_ONLY = True
else:
    USE_MEMORY_ONLY = True

def _get(k: str) -> Optional[str]:
    if USE_MEMORY_ONLY or not redis_client:
        return _mem_get(k)
    try:
        return redis_client.get(k)
    except:
        return _mem_get(k)

def _set(k: str, v: str):
    if USE_MEMORY_ONLY or not redis_client:
        _mem_set(k, v)
        return
    try:
        redis_client.set(k, v)
    except:
        _mem_set(k, v)

# -----------------------------------------------------
# Fetch helper
# -----------------------------------------------------
async def fetch_json(url: str):
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream fetch error: {e}")

# -----------------------------------------------------
# Normalize Functions
# -----------------------------------------------------
def normalize_cfp(teams: Dict[str, Any], ncaa: Dict[str, Any]):
    out = {
        "ts": int(time.time()),
        "teams": [],
        "games": [],
    }

    # Teams
    try:
        raw = teams.get("teams", [])
        for t in raw:
            out["teams"].append({
                "id": t.get("id"),
                "name": t.get("school"),
                "mascot": t.get("mascot"),
                "conference": t.get("conference"),
                "rank": t.get("rank"),
                "record": t.get("record"),
                "logo": t.get("logo"),
            })
    except:
        pass

    # Games
    try:
        sc = ncaa.get("scoreboard", {})
        events = sc.get("games", [])
        for g in events:
            out["games"].append({
                "id": g.get("id"),
                "home": g.get("home", {}).get("names", {}).get("full"),
                "away": g.get("away", {}).get("names", {}).get("full"),
                "start": g.get("startDate"),
                "venue": g.get("venue", {}).get("fullName"),
                "broadcast": g.get("broadcast"),
                "status": g.get("status"),
                "home_score": g.get("home", {}).get("score"),
                "away_score": g.get("away", {}).get("score"),
            })
    except:
        pass

    return out

# -----------------------------------------------------
# LIVE REFRESH ENDPOINT
# -----------------------------------------------------
@router.get("/refresh")
async def refresh():
    teams = await fetch_json(CFP_SOURCE_TEAMS)
    ncaa = await fetch_json(CFP_SOURCE_NCAA)

    combined = normalize_cfp(teams, ncaa)
    _set(CFP_CACHE_KEY, json.dumps(combined))

    return {"ok": True, "updated": combined["ts"]}

# -----------------------------------------------------
# PUBLIC ENDPOINTS
# -----------------------------------------------------
@router.get("/data")
def get_data():
    raw = _get(CFP_CACHE_KEY)
    if not raw:
        raise HTTPException(status_code=404, detail="No CFP data cached. Run /api/cfp/refresh")
    return json.loads(raw)

@router.get("/teams")
def get_teams():
    raw = _get(CFP_CACHE_KEY)
    if not raw:
        raise HTTPException(status_code=404, detail="No CFP data cached.")
    return json.loads(raw).get("teams", [])

@router.get("/games")
def get_games():
    raw = _get(CFP_CACHE_KEY)
    if not raw:
        raise HTTPException(status_code=404, detail="No CFP data cached.")
    return json.loads(raw).get("games", [])

@router.get("/raw")
async def raw_all():
    teams = await fetch_json(CFP_SOURCE_TEAMS)
    ncaa = await fetch_json(CFP_SOURCE_NCAA)
    return {"teams": teams, "ncaa": ncaa}

# -----------------------------------------------------
# TICKETS (StubHub rough feed)
# -----------------------------------------------------
@router.get("/tickets")
async def tickets():
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(CFP_SOURCE_TICKETS)
            try:
                return r.json()
            except:
                return {"text": r.text[:2000]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ticket fetch error: {e}")
