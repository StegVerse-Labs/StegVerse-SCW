"""
StegVerse Ledger Package

Provides core utilities for:
- Loading ledger events from ledger/events/*
- Computing balances
- Producing wallet snapshots and telemetry

This file exists primarily so that 'ledger.*' imports work cleanly in
GitHub Actions and local runs (Python treats 'ledger' as a package).
"""
