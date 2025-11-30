import os
from app.main import app  # this is the SCW FastAPI app in api/app/main.py

# This file is just an entrypoint for Render / uvicorn.
# Render runs: `uvicorn main:app ...` from the /api directory.

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
