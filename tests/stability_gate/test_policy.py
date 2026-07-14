from engine.stability_gate.model import GateInput
from engine.stability_gate.policy import Decision, GatePolicy, evaluate

NOW = 2_000_000_000


def sample(**overrides):
    values = {
        "deliberation_capacity": 1.0,
        "model_fidelity": 1.0,
        "environmental_volatility": 1.0,
        "action_magnitude": 1.0,
        "observed_at": NOW,
        "source": "test",
    }
    values.update(overrides)
    return GateInput(**values)


def test_allow_at_threshold():
    assert evaluate(sample(), now=NOW).decision is Decision.ALLOW


def test_delay_band():
    result = evaluate(sample(deliberation_capacity=0.8), now=NOW)
    assert result.decision is Decision.DELAY


def test_block_below_delay_threshold():
    result = evaluate(sample(deliberation_capacity=0.2), now=NOW)
    assert result.decision is Decision.BLOCK


def test_stale_input_fails_closed():
    result = evaluate(sample(observed_at=NOW - 301), now=NOW)
    assert result.decision is Decision.FAIL_CLOSED


def test_non_finite_input_fails_closed():
    result = evaluate(sample(model_fidelity=float("nan")), now=NOW)
    assert result.decision is Decision.FAIL_CLOSED


def test_invalid_policy_fails_closed():
    policy = GatePolicy(allow_threshold=0.5, delay_threshold=0.7)
    assert evaluate(sample(), policy, now=NOW).decision is Decision.FAIL_CLOSED
