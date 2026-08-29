from pathlib import Path

from finance.coinbase_handler import load_config as load_coinbase
from finance.stripe_handler import load_config as load_stripe


ROOT = Path(__file__).resolve().parents[1]


def test_finance_stub_configs_are_credential_neutral():
    coinbase = load_coinbase()
    stripe = load_stripe()

    assert coinbase.enabled is False
    assert coinbase.api_key is None
    assert coinbase.webhook_secret is None
    assert coinbase.credential_authority == "TV/TVC"
    assert coinbase.provider_route_state == "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED"

    assert stripe.enabled is False
    assert stripe.publishable_key is None
    assert stripe.secret_key is None
    assert stripe.webhook_secret is None
    assert stripe.credential_authority == "TV/TVC"
    assert stripe.provider_route_state == "TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED"


def test_finance_stub_source_does_not_read_provider_secret_environment():
    text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "finance/coinbase_handler.py",
            "finance/stripe_handler.py",
            "finance/payments_config.example.json",
        )
    )
    for marker in (
        "COINBASE_COMMERCE_API_KEY",
        "COINBASE_COMMERCE_WEBHOOK_SECRET",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "GitHub secrets",
        "os.getenv",
    ):
        assert marker not in text
