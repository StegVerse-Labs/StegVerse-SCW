# StegVerse-SCW/api/main.py
"""
Thin shim so process managers can use `main:app` while the real
FastAPI application lives in `api/app/main.py`.
"""

from app.main import app  # noqa: F401

__all__ = ["app"]
