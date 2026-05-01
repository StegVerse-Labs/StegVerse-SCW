from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from math import sqrt
from typing import Any, Dict, List, Optional
import json
import uuid

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


def build_receipt(
    *,
    version: int,
    kind: str,
    body: Dict[str, Any],
    previous_receipt_hash: Optional[str] = None,
) -> Dict[str, Any]:
    envelope = {
        "schema": "stegverse.receipt",
        "version": version,
        "kind": kind,
        "previous_receipt_hash": previous_receipt_hash,
        "body": body,
    }
    return {
        **envelope,
        "receipt_hash": hash_obj(envelope),
    }


def evaluate_boundary(payload: DemoRun) -> Dict[str, Any]:
    states = payload.commit_states
    proposed = payload.proposed_state

    if len(states) < 2:
        return {
            "verdict": "FAIL-CLOSED",
            "reason": "At least two commit states are required.",
            "god": 999.0,
            "confidence": 0.0,
            "boundary": {"centroid": [], "radius": 0.0, "epsilon": 0.0},
        }

    if not proposed:
        return {
            "verdict": "FAIL-CLOSED",
            "reason": "Proposed state is empty.",
            "god": 999.0,
            "confidence": 0.0,
            "boundary": {"centroid": [], "radius": 0.0, "epsilon": 0.0},
        }

    if any(len(s) != len(proposed) for s in states):
        return {
            "verdict": "FAIL-CLOSED",
            "reason": "Commit state dimensions do not match proposed state.",
            "god": 999.0,
            "confidence": 0.0,
            "boundary": {"centroid": [], "radius": 0.0, "epsilon": 0.0},
        }

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
        "reason": "Commit-boundary admissibility evaluated.",
        "god": god,
        "confidence": confidence,
        "boundary": {
            "centroid": [round(x, 12) for x in centroid],
            "radius": round(radius, 12),
            "epsilon": round(epsilon, 12),
        },
    }


def local_test_runner(
    *,
    payload_dict: Dict[str, Any],
    decision_hash: str,
    decision_receipt_hash: str,
) -> Dict[str, Any]:
    executed_at = utc_now()
    execution_id = f"exec_{uuid.uuid4().hex}"

    result = {
        "status": "executed",
        "runner": "local_test_runner",
        "effect": "no_external_side_effect",
        "demo_id": payload_dict.get("demo_id", "unknown"),
    }

    body = {
        "execution_id": execution_id,
        "runner": "local_test_runner",
        "mode": "local_tier2_test_harness",
        "input_hash": hash_obj(payload_dict),
        "decision_hash": decision_hash,
        "decision_receipt_hash": decision_receipt_hash,
        "output_hash": hash_obj(result),
        "executed_at": executed_at,
    }

    receipt = build_receipt(
        version=1,
        kind="local_runner_execution",
        previous_receipt_hash=decision_receipt_hash,
        body=body,
    )

    return {
        "attempted": True,
        "ok": True,
        "mode": "local_test_runner",
        "result": result,
        "runner_receipt": receipt,
        "runner_receipt_hash": receipt["receipt_hash"],
    }


@router.get("/v1/demo/health")
def demo_health() -> Dict[str, Any]:
    return {
        "ok": True,
        "service": "stegverse-demo-tier1-tier2-local",
        "tier_1": "commit_boundary_admissibility",
        "tier_2": "local_test_runner_receipt_only_for_ALLOW",
        "runner_binding": "local_test_harness_not_external_runner",
    }


@router.post("/v1/demo/run")
def run_demo(payload: DemoRun) -> Dict[str, Any]:
    evaluated_at = utc_now()
    payload_dict = model_to_dict(payload)
    input_hash = hash_obj(payload_dict)
    decision_id = f"dec_{uuid.uuid4().hex}"

    tier1 = evaluate_boundary(payload)

    decision_record = {
        "decision_id": decision_id,
        "decision": tier1["verdict"],
        "reason": tier1["reason"],
        "god": round(tier1["god"], 12),
        "confidence": round(tier1["confidence"], 12),
        "boundary": tier1["boundary"],
        "input_hash": input_hash,
        "evaluated_at": evaluated_at,
    }

    decision_hash = hash_obj(decision_record)

    receipt_v1 = build_receipt(
        version=1,
        kind="commit_boundary_decision",
        previous_receipt_hash=None,
        body={
            "decision_id": decision_id,
            "decision": tier1["verdict"],
            "reason": tier1["reason"],
            "source": payload.source,
            "demo_id": payload.demo_id,
            "input_hash": input_hash,
            "decision_hash": decision_hash,
            "evaluated_at": evaluated_at,
        },
    )

    receipt_v2 = build_receipt(
        version=2,
        kind="commit_boundary_decision",
        previous_receipt_hash=None,
        body={
            "decision_id": decision_id,
            "decision": tier1["verdict"],
            "reason": tier1["reason"],
            "source": payload.source,
            "demo_id": payload.demo_id,
            "input_hash": input_hash,
            "decision_hash": decision_hash,
            "boundary_hash": hash_obj(tier1["boundary"]),
            "god": round(tier1["god"], 12),
            "confidence": round(tier1["confidence"], 12),
            "evaluated_at": evaluated_at,
        },
    )

    if tier1["verdict"] == "ALLOW":
        tier2 = local_test_runner(
            payload_dict=payload_dict,
            decision_hash=decision_hash,
            decision_receipt_hash=receipt_v2["receipt_hash"],
        )
    else:
        tier2 = {
            "attempted": False,
            "ok": True,
            "reason": "Tier 2 execution is only invoked after Tier 1 ALLOW.",
        }

    receipt_v2["body"]["tier2_attempt_hash"] = hash_obj(tier2)
    receipt_v2["body"]["tier2_runner_receipt_hash"] = tier2.get("runner_receipt_hash")

    receipts = [receipt_v2, receipt_v1]
    if tier2.get("runner_receipt"):
        receipts.append(tier2["runner_receipt"])

    return {
        "verdict": tier1["verdict"],
        "god": tier1["god"],
        "confidence": tier1["confidence"],
        "boundary": tier1["boundary"],
        "receipt": receipt_v2["receipt_hash"],
        "receipt_full": receipt_v2,
        "receipt_v1": receipt_v1,
        "tier1": {
            "decision_hash": decision_hash,
            "receipt_hash": receipt_v2["receipt_hash"],
            "receipt": receipt_v2,
        },
        "tier2": tier2,
        "receipts": receipts,
    }
