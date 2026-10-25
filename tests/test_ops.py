import json
import os
import time
import urllib.request

import pytest

API_BASE = os.environ.get("API_BASE")  # e.g. https://your-api.example
TIMEOUT  = float(os.environ.get("E2E_TIMEOUT_SEC", "60"))
POLL_EVERY = float(os.environ.get("E2E_POLL_SEC", "3"))

pytestmark = pytest.mark.skipif(not API_BASE, reason="Set API_BASE env var to live API URL")

def _get(url):
    # urlopen raises HTTPError on any 4xx/5xx status, like raise_for_status().
    with urllib.request.urlopen(url, timeout=30.0) as r:
        return json.loads(r.read().decode("utf-8"))

def _post(url, payload=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload or {}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30.0) as r:
        return json.loads(r.read().decode("utf-8"))

def test_health():
    data = _get(f"{API_BASE}/v1/ops/health")
    assert data.get("status") == "ok"

def test_env_required():
    data = _get(f"{API_BASE}/v1/ops/env/required")
    # we expect at least these keys to be present (True/False)
    present = data.get("present", {})
    assert "REDIS_URL" in present
    assert "RUNS_QUEUE_KEY" in present

def test_enqueue_and_process():
    # 1) baseline metrics
    before = _get(f"{API_BASE}/v1/ops/metrics")
    processed_before = int(before.get("processed", 0))

    # 2) enqueue a synthetic job
    resp = _post(f"{API_BASE}/v1/ops/queue/test")
    assert resp.get("queued") is True

    # 3) poll until processed increases
    deadline = time.time() + TIMEOUT
    processed_after = processed_before
    while time.time() < deadline:
        time.sleep(POLL_EVERY)
        now = _get(f"{API_BASE}/v1/ops/metrics")
        processed_after = int(now.get("processed", 0))
        if processed_after > processed_before:
            break

    assert processed_after > processed_before, (
        f"Worker did not process job within {TIMEOUT}s. "
        f"before={processed_before} after={processed_after}"
    )
