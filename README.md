# StegVerse SCW (StegVerse Code Worker)

SCW is the StegVerse root orchestrator. It receives commands (via workflow_dispatch or /scw issue comments),
runs validations, and will progressively host Guardians (Autopatch, Readme, Governance, Continuity, Deploy).

## Workflows

- **SCW Orchestrator**: `.github/workflows/scw_orchestrator.yml`
  - Run from Actions tab.
  - Commands: `self-test`, `autopatch`, `sync-templates`, `standardize-readme`.

- **SCW Bridge**: `.github/workflows/scw_bridge.yml`
  - Listen for `/scw <command> [json]` in issues/comments in any repo.

## Setup

1. Ensure org secret `GH_STEGVERSE_AI_TOKEN` exists in **StegVerse-Labs**.
2. Ensure repos are public or org plan allows org secrets for private repos.
3. Run **SCW Orchestrator → self-test**.

## Roadmap

Phase 2 will add real template syncing and autopatch PR generation.

## Operations

<!-- ops:console -->
**Ops Console** — quick links (hybrid):

[Open full console](.github/docs/WORKFLOWS_CONSOLE.md) · [All Actions](https://github.com/StegVerse-Labs/StegVerse-SCW/actions)

| Workflow | State | Actions |
|---|---|---|
| `AutoPatch.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/AutoPatch.yml) · [File](.github/workflows/AutoPatch.yml) |
| `actions-permission-check.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/actions-permission-check.yml) · [File](.github/workflows/actions-permission-check.yml) |
| `alignment_check.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/alignment_check.yml) · [File](.github/workflows/alignment_check.yml) |
| `alignment_fixer.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/alignment_fixer.yml) · [File](.github/workflows/alignment_fixer.yml) |
| `auto_patch.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/auto_patch.yml) · [File](.github/workflows/auto_patch.yml) |
| `autodocs-on-demand.yml` | ❌ broken · `ScannerError` | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autodocs-on-demand.yml) · [File](.github/workflows/autodocs-on-demand.yml) |
| `autopatch-inspect.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch-inspect.yml) · [File](.github/workflows/autopatch-inspect.yml) |
| `autopatch-ops.yml` | ❌ broken · `ScannerError` | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch-ops.yml) · [File](.github/workflows/autopatch-ops.yml) |
| `autopatch-readme-quickcontrols.yml` | ❌ broken · `ScannerError` | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch-readme-quickcontrols.yml) · [File](.github/workflows/autopatch-readme-quickcontrols.yml) |
| `autopatch-reindex.yml` | ❌ broken · `ScannerError` | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch-reindex.yml) · [File](.github/workflows/autopatch-reindex.yml) |
| `autopatch-repotree-and-supercheck.yml` | ❌ broken · `ScannerError` | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch-repotree-and-supercheck.yml) · [File](.github/workflows/autopatch-repotree-and-supercheck.yml) |
| `autopatch-wire-ops-table-links.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch-wire-ops-table-links.yml) · [File](.github/workflows/autopatch-wire-ops-table-links.yml) |

_See the full table for all workflows → [.github/docs/WORKFLOWS_CONSOLE.md](.github/docs/WORKFLOWS_CONSOLE.md)._
<!-- /ops:console -->
