# api/routes/ops.py
import os
from typing import Optional

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/v1/ops", tags=["ops"])

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

def _auth(token: Optional[str]):
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=501, detail="admin ops not configured")
    if not token or token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="forbidden")

@router.get("/snapshot")
def snapshot():
    return {"ok": True, "service": "ops", "env": {"SCW_API_URL": os.getenv("SCW_API_URL")}}
