from fastapi import APIRouter
from datetime import datetime
from hashlib import sha256
import json
import uuid
from math import sqrt

router = APIRouter()


def dist(a, b):
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def hash_obj(obj):
    return sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


@router.get("/v1/demo/health")
def health():
    return {"ok": True}


@router.post("/v1/demo/run")
def run_demo(payload: dict):
    states = payload.get("commit_states", [])
    proposed = payload.get("proposed_state", [])

    if len(states) < 2 or not proposed:
        return {"verdict": "FAIL-CLOSED"}

    centroid = [sum(s[i] for s in states)/len(states) for i in range(len(proposed))]
    radius = max(dist(s, centroid) for s in states)
    epsilon = max(0.01, radius * 0.05)

    d = dist(proposed, centroid)
    god = d / (radius + epsilon)

    if god <= 1:
        verdict = "ALLOW"
    elif god <= 1.35:
        verdict = "DENY"
    else:
        verdict = "FAIL-CLOSED"

    record = {
        "decision_id": str(uuid.uuid4()),
        "verdict": verdict,
        "god": god,
        "evaluated_at": datetime.utcnow().isoformat()
    }

    return {
        "verdict": verdict,
        "god": god,
        "receipt": sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
    }
