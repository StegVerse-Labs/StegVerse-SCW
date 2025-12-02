from fastapi import FastAPI
from app.main import app as real_app

# Create a wrapper app just to expose /healthz
wrapper = FastAPI()

@wrapper.get("/healthz")
def healthz():
    return {"ok": True}

# Mount your real app at root
wrapper.mount("/", real_app)

app = wrapper
