# SCW-STUB api/main.py v2025-12-02-02
"""
Entry stub so that `uvicorn main:app` (used by Render) loads the real SCW API
from `api/app/main.py`, and exposes `/healthz` for Render's health checks.
"""

from app.main import app  # noqa: F401


@app.get("/healthz")
def healthz():
    """
    Lightweight health endpoint for Render.

    Returns 200 OK with a simple payload. The real internal health remains
    at `/v1/ops/health` inside the SCW app.
    """
    return {"ok": True, "source": "scw-stub"}
