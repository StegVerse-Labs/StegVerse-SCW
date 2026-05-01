from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from math import sqrt
from typing import Any, Dict, List, Optional
import json
import os
import uuid

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter()


class DemoRun(BaseModel):
    source: str = Field(default="unknown")
    demo_id: str = Field(default_factory=lambda: f"demo_{uuid.uuid4().hex[:12]}")
    commit_states: List[List[float]]
    proposed_state: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()  # type: ignore[attr-defined]
    return model.dict()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_obj(obj: Any) -> str:
    return sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def distance(a: List[float], b: List[float]) -> float:
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def build_receipt_v1(
    *,
    decision_id: str,
    decision: str,
    reason: str,
    source: str,
    demo_id: str,
    input_hash: str,
    decision_hash: str,
    runner_attempt: Dict[str, Any],
    evaluated_at: str,
) -> Dict[str, Any]:
    body = {
        "decision_id": decision_id,
        "decision": decision,
        "reason": reason,
        "source": source,
        "demo_id": demo_id,
        "input_hash": input_hash,
        "decision_hash": decision_hash,
        "runner_attempt": runner_attempt,
        "evaluated_at": evaluated_at,
    }

    envelope = {
        "schema": "stegverse.receipt",
        "version": 1,
        "kind": "commit_boundary_decision",
        "previous_receipt_hash": None,
        "body": body,
    }

    return {
        **envelope,
        "receipt_hash": hash_obj(envelope),
    }


def build_receipt_v2(
    *,
    decision_id: str,
    decision: str,
    reason: str,
    source: str,
    demo_id: str,
    input_hash: str,
    decision_hash: str,
    runner_attempt: Dict[str, Any],
    boundary: Dict[str, Any],
    god: float,
    confidence: float,
    evaluated_at: str,
) -> Dict[str, Any]:
    runner_receipt_hash = runner_attempt.get("runner_receipt_hash")
    if not runner_receipt_hash:
        runner_receipt_hash = hash_obj(runner_attempt)

    body = {
        "decision_id": decision_id,
        "decision": decision,
        "reason": reason,
        "source": source,
        "demo_id": demo_id,
        "input_hash": input_hash,
        "decision_hash": decision_hash,
        "boundary_hash": hash_obj(boundary),
        "runner_attempt_hash": hash_obj(runner_attempt),
        "runner_receipt_hash": runner_receipt_hash,
        "god": round(god, 12),
        "confidence": round(confidence, 12),
        "evaluated_at": evaluated_at,
    }

    envelope = {
        "schema": "stegverse.receipt",
        "version": 2,
        "kind": "commit_boundary_decision",
        "previous_receipt_hash": None,
        "body": body,
    }

    return {
        **envelope,
        "receipt_hash": hash_obj(envelope),
    }


def build_response(
    *,
    verdict: str,
    god: float,
    confidence: float,
    boundary: Dict[str, Any],
    receipt_v2: Dict[str, Any],
    receipt_v1: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "verdict": verdict,
        "god": god,
        "confidence": confidence,
        "boundary": boundary,

        # Permanent legacy contract: always a string hash.
        "receipt": receipt_v2["receipt_hash"],

        # Primary modern receipt.
        "receipt_full": receipt_v2,

        # Compatibility projection.
        "receipt_v1": receipt_v1,

        # Future-safe multi-receipt surface.
        "receipts": [receipt_v2, receipt_v1],
    }


def build_fail_closed_response(
    payload: Any,
    reason: str,
    runner_attempt: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    evaluated_at = utc_now()
    input_hash = hash_obj(payload)
    decision_id = f"dec_{uuid.uuid4().hex}"

    boundary = {
        "centroid": [],
        "radius": 0.0,
        "epsilon": 0.0,
    }

    runner_attempt_final = runner_attempt or {"attempted": False}

    decision_record = {
        "decision": "FAIL-CLOSED",
        "reason": reason,
        "input_hash": input_hash,
        "boundary": boundary,
        "runner_attempt_hash": hash_obj(runner_attempt_final),
        "evaluated_at": evaluated_at,
    }

    decision_hash = hash_obj(decision_record)

    receipt_v1 = build_receipt_v1(
        decision_id=decision_id,
        decision="FAIL-CLOSED",
        reason=reason,
        source="unknown",
        demo_id="unknown",
        input_hash=input_hash,
        decision_hash=decision_hash,
        runner_attempt=runner_attempt_final,
        evaluated_at=evaluated_at,
    )

    receipt_v2 = build_receipt_v2(
        decision_id=decision_id,
        decision="FAIL-CLOSED",
        reason=reason,
        source="unknown",
        demo_id="unknown",
        input_hash=input_hash,
        decision_hash=decision_hash,
        runner_attempt=runner_attempt_final,
        boundary=boundary,
        god=999.0,
        confidence=0.0,
        evaluated_at=evaluated_at,
    )

    return build_response(
        verdict="FAIL-CLOSED",
        god=999.0,
        confidence=0.0,
        boundary=boundary,
        receipt_v2=receipt_v2,
        receipt_v1=receipt_v1,
    )


def evaluate_boundary(payload: DemoRun) -> Dict[str, Any]:
    payload_dict = model_to_dict(payload)
    states = payload.commit_states
    proposed = payload.proposed_state

    if len(states) < 2:
        return build_fail_closed_response(
            payload_dict,
            "At least two commit states are required.",
        )

    if not proposed:
        return build_fail_closed_response(
            payload_dict,
            "Proposed state is empty.",
        )

    if any(len(s) != len(proposed) for s in states):
        return build_fail_closed_response(
            payload_dict,
            "Commit state dimensions do not match proposed state.",
        )

    dims = len(proposed)
    centroid = [sum(s[i] for s in states) / len(states) for i in range(dims)]
    radius = max(distance(s, centroid) for s in states)
    epsilon = max(0.01, radius * 0.05)
    proposed_distance = distance(proposed, centroid)
    effective_radius = radius + epsilon
    god = proposed_distance / effective_radius if effective_radius else 999.0

    if god <= 1.0:
        verdict = "ALLOW"
    elif god <= 1.35:
        verdict = "DENY"
    else:
        verdict = "FAIL-CLOSED"

    confidence = max(0.0, min(1.0, 1.0 - abs(god - 1.0) / 1.35))

    return {
        "verdict": verdict,
        "god": god,
        "confidence": confidence,
        "boundary": {
            "centroid": [round(x, 12) for x in centroid],
            "radius": round(radius, 12),
            "epsilon": round(epsilon, 12),
        },
    }


def call_runner(payload: DemoRun, local_decision: Dict[str, Any]) -> Dict[str, Any]:
    runner_url = os.getenv("STEGVERSE_RUNNER_URL", "").rstrip("/")
    runner_token = os.getenv("STEGVERSE_RUNNER_TOKEN", "")

    if not runner_url:
        return {
            "attempted": False,
            "reason": "STEGVERSE_RUNNER_URL is not configured.",
        }

    body = {
        "source": "scw_demo_api",
        "demo_id": payload.demo_id,
        "input": model_to_dict(payload),
        "local_decision": local_decision,
    }

    headers = {"Content-Type": "application/json"}
    if runner_token:
        headers["Authorization"] = f"Bearer {runner_token}"

    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.post(runner_url, headers=headers, json=body)

        try:
            data = response.json()
        except Exception:
            data = {}

        runner_receipt = data.get("receipt") or data.get("receipt_full")

        if runner_receipt:
            return {
                "attempted": True,
                "ok": response.is_success,
                "status_code": response.status_code,
                "runner_receipt": runner_receipt,
                "runner_receipt_hash": hash_obj(runner_receipt),
            }

        return {
            "attempted": True,
            "ok": response.is_success,
            "status_code": response.status_code,
            "non_compliant": True,
            "response_hash": hash_obj(response.text),
            "response_preview": response.text[:500],
        }

    except Exception as exc:
        return {
            "attempted": True,
            "ok": False,
            "error": str(exc),
        }


@router.get("/v1/demo/health")
def demo_health() -> Dict[str, Any]:
    return {
        "ok": True,
        "service": "stegverse-demo-tier1",
        "receipt_contract": {
            "receipt": "string hash, stable legacy field",
            "receipt_full": "primary receipt envelope",
            "receipt_v1": "v1 compatibility projection",
            "receipts": "array of available receipt envelopes",
        },
        "primary_receipt_version": 2,
        "runner_configured": bool(os.getenv("STEGVERSE_RUNNER_URL", "")),
    }


@router.post("/v1/demo/run")
def run_demo(payload: DemoRun) -> Dict[str, Any]:
    local_decision = evaluate_boundary(payload)

    # Malformed input already produced a complete fail-closed response.
    if "receipt_full" in local_decision:
        return local_decision

    if local_decision["verdict"] != "ALLOW":
        runner_attempt = {
            "attempted": False,
            "reason": "Runner is only invoked after local commit-boundary ALLOW.",
        }
    else:
        runner_attempt = call_runner(payload, local_decision)

    evaluated_at = utc_now()
    payload_dict = model_to_dict(payload)
    input_hash = hash_obj(payload_dict)
    decision_id = f"dec_{uuid.uuid4().hex}"

    decision_record = {
        "decision": local_decision["verdict"],
        "god": round(local_decision["god"], 12),
        "confidence": round(local_decision["confidence"], 12),
        "boundary": local_decision["boundary"],
        "runner_attempt_hash": hash_obj(runner_attempt),
        "input_hash": input_hash,
        "evaluated_at": evaluated_at,
    }

    decision_hash = hash_obj(decision_record)

    reason = "Commit-boundary admissibility evaluated before runner invocation."

    receipt_v1 = build_receipt_v1(
        decision_id=decision_id,
        decision=local_decision["verdict"],
        reason=reason,
        source=payload.source,
        demo_id=payload.demo_id,
        input_hash=input_hash,
        decision_hash=decision_hash,
        runner_attempt=runner_attempt,
        evaluated_at=evaluated_at,
    )

    receipt_v2 = build_receipt_v2(
        decision_id=decision_id,
        decision=local_decision["verdict"],
        reason=reason,
        source=payload.source,
        demo_id=payload.demo_id,
        input_hash=input_hash,
        decision_hash=decision_hash,
        runner_attempt=runner_attempt,
        boundary=local_decision["boundary"],
        god=local_decision["god"],
        confidence=local_decision["confidence"],
        evaluated_at=evaluated_at,
    )

    return build_response(
        verdict=local_decision["verdict"],
        god=local_decision["god"],
        confidence=local_decision["confidence"],
        boundary=local_decision["boundary"],
        receipt_v2=receipt_v2,
        receipt_v1=receipt_v1,
    )
