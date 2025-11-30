# api/routes/routes_cfp.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/v1/sports", tags=["sports"])

@router.get("/cfp/current")
async def get_cfp_current():
    # TODO: replace this with real data from a sports API or DB
    return {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "sources": [
            {"id": "1", "label": "College Football Playoff", "url": "https://collegefootballplayoff.com"},
            {"id": "2", "label": "AP Top 25", "url": "https://apnews.com"},
            {"id": "3", "label": "Coaches Poll", "url": "https://sports.usatoday.com"},
            {"id": "4", "label": "ESPN Standings", "url": "https://espn.com/college-football/standings"}
        ],
        "cfp_source_id": "1",
        "conf_source_id": "4",
        "rankings": [],
        "games": [],
        "polls": [],
        "conferences": []
    }
