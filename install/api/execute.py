from fastapi import APIRouter, Request
from datetime import datetime, timezone
from hashlib import sha256
import json
import uuid

router = APIRouter()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def h(obj):
    return sha256(canonical(obj).encode()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

@router.post("/execute")
async def execute(req: Request):
    payload = await req.json()

    execution_id = f"exec_{uuid.uuid4().hex}"

    # Minimal "execution" (no-op but deterministic)
    result = {
        "status": "executed",
        "echo": payload.get("input", {})
    }

    input_hash = h(payload)
    output_hash = h(result)

    receipt_body = {
        "execution_id": execution_id,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "timestamp": now(),
    }

    receipt = {
        "schema": "stegverse.receipt",
        "version": 1,
        "kind": "runner_execution",
        "previous_receipt_hash": None,
        "body": receipt_body,
    }

    return {
        "result": result,
        "receipt": {
            **receipt,
            "receipt_hash": h(receipt)
        }
    }
