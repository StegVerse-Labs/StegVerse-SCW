# api/app/main.py
"""
Shim module so anything importing `api.app.main:app`
gets the same FastAPI instance as `api.main:app`.

Render and all tooling should treat `api.main` as the single
source of truth for the SCW API.
"""

from api.main import app  # type: ignore

__all__ = ["app"]
