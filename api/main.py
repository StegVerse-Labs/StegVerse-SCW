# StegVerse-SCW/api/main.py
import os
from app.main import app  # FastAPI instance

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )
