# SCW Finance Provider Credential Boundary Mirror Handoff

## Source of truth

This file owns only the Stripe/Coinbase Commerce shape-only finance credential boundary in `StegVerse-Labs/StegVerse-SCW`.

## Finding

Historical shape-only finance handlers still read protected provider values from the SCW environment:

```text
finance/stripe_handler.py
  STRIPE_SECRET_KEY
  STRIPE_WEBHOOK_SECRET

finance/coinbase_handler.py
  COINBASE_COMMERCE_API_KEY
  COINBASE_COMMERCE_WEBHOOK_SECRET
```

Consumer-side secret materialization conflicts with TV/TVC-only credential authority even before provider execution exists.

## Repair boundary

```text
credential authority: TV/TVC
SCW finance credential authority: NONE
consumer environment secret reads: RETIRED_ON_BRANCH
consumer secret materialization: FALSE
Stripe provider execution: NOT IMPLEMENTED / NOT OBSERVED
Coinbase Commerce provider execution: NOT IMPLEMENTED / NOT OBSERVED
replacement state: TVC_ADMITTED_PROVIDER_ROUTE_REQUIRED
authority_effect: NONE
```

## Lifecycle

```text
source repair: IMPLEMENTED_ON_BRANCH
validation: PENDING
merge: PENDING
provider runtime activation: NOT OBSERVED
```
