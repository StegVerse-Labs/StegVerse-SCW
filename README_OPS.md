# StegVerse-SCW — Ops & Recovery Guide

This document explains how to operate, recover, and redeploy the **SCW** (Sandbox Code Writer) stack:
- **API** (FastAPI)
- **UI** (Next.js)
- **Worker** (queue processor; Redis-backed)
- **Edge/site providers** (Cloudflare, Netlify, Vercel)
- The **Admin Token** lifecycle (bootstrap → normal ops → recovery)
- The **One-Click Reset & Redeploy** flow

---

## Contents
- [Architecture Overview](#architecture-overview)
- [Security Model](#security-model)
- [Environment & Config Keys](#environment--config-keys)
- [Endpoints (Ops API)](#endpoints-ops-api)
- [Diagnostics Page (`/diag.html`)](#diagnostics-page-diaghtml)
- [Common Flows](#common-flows)
  - [First-time Bootstrap](#first-time-bootstrap)
  - [Normal Operations](#normal-operations)
  - [Lost Admin Token (Recovery)](#lost-admin-token-recovery)
  - [One-Click Reset & Redeploy](#one-click-reset--redeploy)
  - [Worker State Reset](#worker-state-reset)
  - [Cloudflare Rotate/Purge](#cloudflare-rotatepurge)
- [Curl Cheat Sheet](#curl-cheat-sheet)
- [Troubleshooting](#troubleshooting)
- [Operational Checklists](#operational-checklists)
- [Addendum: Repo Pointers & UI Autodetect](#addendum-repo-pointers--ui-autodetect)

---

## Architecture Overview

## Enterprise provider eradication (2026-10-22)

Under parent `ENTERPRISE-HOST-PROVIDER-ERADICATION-001` / COSV `40000100100000` and StegHealth intake #82, the proposed owner branch removes a named third-party hosting example from the read-only supercheck workflow. The optional API check requires an explicitly supplied, authorized URL; no provider is selected by default. This limited source repair does not verify other SCW provider hooks, exact-head CI, native admission, sovereign readback or provider account shutdown. No replacement host or external machine is introduced.
