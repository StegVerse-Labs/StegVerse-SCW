# StegVerse HyperCore v1.0

This document defines the "living spine" of StegVerse, covering:

- Phase 1: Core fusion (SCW, TVC, HCB, Continuity, layout)
- Phase 2: AI workforce (worker classes)
- Phase 3: Payments + revenue
- Phase 4: Compliance engine
- Phase 5: StegWallet, StegToken, StegLedger
- Phase 6: Hybrid evolution around Rigel (the human operator)

---

## Phase 1 — Core Fusion

Core components:

- StegCore / SCW (this repo): self-healing, autopatch, audits, orchestration
- StegTVC: model/route resolver (cost-aware)
- Hybrid-Collab-Bridge: AI worker gateway
- Continuity: global timeline + audit + intent log
- Layout Normalizer: file/path/name sanity (cross-repo)

This repo is the **control plane** for rules, manifests, and cross-repo actions.

---

## Phase 2 — AI Workforce

Worker classes (see `core/worker_registry.yaml`):

- infra: workflows, layout, deps, basic fixes
- builder: features, modules, docs, tests
- compliance: policies, permissions, boundaries
- economy: payments, wallets, ledgers, fraud signals

Workers run through Hybrid-Collab-Bridge + TVC routing, under SCW control.

---

## Phase 3 — Payments & Revenue

Payment integration (see `finance/`):

- Stripe: card/ACH/subscription billing (fiat)
- Coinbase Commerce: crypto payments (BTC/ETH/USDC)
- Future: MetaMask / WalletConnect → DeFi bridges

Core principles:

- Payment secrets live in vault (StegTV)
- All payment events are logged to Continuity
- Economy workers score risk + anomalies

---

## Phase 4 — Compliance Engine v1

Compliance definitions (see `compliance/`):

- compliance_rules.yaml → rules for privacy, finance, AI behavior
- risk_register.md → known risks, mitigations, open items

Key guarantees:

- Every financial or sensitive action has:
  - identity (who/what)
  - intent (why)
  - decision log (how)
  - outcome (what happened)

---

## Phase 5 — StegWallet, StegToken, StegLedger

Located in `ledger/`:

- steg_wallet.py → unified view of fiat, crypto, StegTokens
- steg_token.py  → internal token model (mint/burn/lock)
- steg_ledger.py → append-only event log (payments, grants, wages, etc.)

Goal:

- Make StegVerse economically self-contained over time.
- Let AI workers earn/pay in StegToken.
- Ensure all flows are auditable.

---

## Phase 6 — Hybrid Evolution

Design constraint:

> The system MUST evolve with Rigel’s physical, mental, and spiritual bandwidth.

Practical rules:

- No single human is a SPOF.
- The system gets *simpler* for Rigel as it gets more complex inside.
- The system protects Rigel’s financial + mental health.
- Workflows are mobile-friendly and safe to trigger from a phone.

This doc is the anchor. All major changes should update this file.
