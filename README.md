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

The historical `GH_STEGVERSE_AI_TOKEN` bridge-dispatch setup is retired. GitHub Actions is validation/evidence transport only and must not hold cross-repository command or mutation authority.

Bridge continuation requires an already-admitted TV/TVC transport capability with exact caller, target, operation, and secret-free receipt evidence. Until that route is present, bridge forwarding remains fail-closed as `TVC_ADMITTED_TRANSPORT_REQUIRED`.

### ASL-1 repository alignment

The repository-alignment checker is credential-free **and stdlib-only**. `scripts/genesis/guardian_repo_alignment_check.py` must not fetch repositories, inspect provider secrets, resolve `PAT_WORKFLOW`, `GH_STEGVERSE_PAT`, `GITHUB_TOKEN`, or equivalent credentials, or require PyYAML merely to read its policy.

The canonical policy path remains `docs/governance/repo_alignment_expectations.yaml` for compatibility with existing SCW surfaces, but its bytes are JSON serialization. JSON is valid YAML, so legacy YAML-capable readers remain compatible while the checker parses the policy with Python's standard-library `json` module and has no PyYAML prerequisite.

Before ASL-1 evaluation, every configured target repository must already have been materialized by an admitted TV/TVC exact-source read path. The checker accepts a secret-free materialization manifest that binds each target to its repository identity, exact 40-character commit SHA, local materialized path, receipt reference, and `authority=TV/TVC`. Secret-, token-, password-, PAT-, or credential-bearing manifest fields fail closed.

The checker evaluates only those local snapshots and writes `reports/guardians/repo_alignment_latest.json` and `reports/guardians/repo_alignment_latest.md`. Source materialization, report publication, repository mutation, release, deployment, runtime, or production authority are separate governed capabilities and are not created by ASL-1 evaluation. `.github/workflows/alignment_check.yml` remains contained until the required admitted source-materialization and any separately required publication predicates are satisfied.

### TaskOps nightly validation

`.github/workflows/taskops-nightly.yml` is a scheduled/manual **validation and evidence-transport** surface only. It runs the existing AutoDocs probe against the checked-out repository, captures any proposed `README.md` / `.github/docs/` delta as `taskops-proposed.patch`, and retains the proposed outputs as a workflow artifact.

The TaskOps workflow has `contents: read`, does not persist checkout credentials, does not configure a bot identity, and must not commit or push generated documentation to `main`. The historical call to the absent `scripts/readme_ci_dashboard.py` is retired. Artifact generation does not authorize repository mutation or publication; applying proposed documentation requires a separately admitted bounded mutation/publication path.

## Roadmap

Phase 2 will add real template syncing and autopatch PR generation.

## Operations

<!-- ops:console -->
**Ops Console** — quick links (hybrid):

[Open full console](.github/docs/WORKFLOWS_CONSOLE.md) · [All Actions](https://github.com/StegVerse-Labs/StegVerse-SCW/actions)

| Workflow | State | Actions |
|---|---|---|
| `00_repo_scanner.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/00_repo_scanner.yml) · [File](.github/workflows/00_repo_scanner.yml) |
| `AutoPatch.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/AutoPatch.yml) · [File](.github/workflows/AutoPatch.yml) |
| `actions-permission-check.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/actions-permission-check.yml) · [File](.github/workflows/actions-permission-check.yml) |
| `alignment_check.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/alignment_check.yml) · [File](.github/workflows/alignment_check.yml) |
| `alignment_fixer.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/alignment_fixer.yml) · [File](.github/workflows/alignment_fixer.yml) |
| `auto_patch.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/auto_patch.yml) · [File](.github/workflows/auto_patch.yml) |
| `autodocs-on-demand.yml` | ❌ broken · `ScannerError` | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autodocs-on-demand.yml) · [File](.github/workflows/autodocs-on-demand.yml) |
| `autopatch-inspect.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch-inspect.yml) · [File](.github/workflows/autopatch-inspect.yml) |
| `autopatch-wire-ops-table-links.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch-wire-ops-table-links.yml) · [File](.github/workflows/autopatch-wire-ops-table-links.yml) |
| `autopatch.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch.yml) · [File](.github/workflows/autopatch.yml) |
| `autopatch_apply.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch_apply.yml) · [File](.github/workflows/autopatch_apply.yml) |
| `autopatch_deferred.yml` | ➖ no-dispatch | [Run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/workflows/autopatch_deferred.yml) · [File](.github/workflows/autopatch_deferred.yml) |

_See the full table for all workflows → [.github/docs/WORKFLOWS_CONSOLE.md](.github/docs/WORKFLOWS_CONSOLE.md)._
<!-- /ops:console -->

## CI Coverage

<!-- pr-safe-status:start -->
_This table is auto-generated by AutoDocs._

| Workflow / Job | PR-safe dispatcher |
|---|---|
| `00_repo_scanner.yml` | not-inserted |
| `AutoPatch.yml` | not-inserted |
| `actions-permission-check.yml` | not-inserted |
| `alignment_check.yml` | not-inserted |
| `alignment_fixer.yml` | not-inserted |
| `auto_patch.yml` | not-inserted |
| `autodocs-on-demand.yml` | parse-failed |
| `autopatch-inspect.yml` | not-inserted |
| `autopatch-wire-ops-table-links.yml` | not-inserted |
| `autopatch.yml` | not-inserted |
| `autopatch_apply.yml` | not-inserted |
| `autopatch_deferred.yml` | not-inserted |
| `autopatch_dryrun.yml` | parse-failed |
| `autopatch_stegtv_connectivity.yml` | not-inserted |
| `backup_triggers.yml` | not-inserted |
| `ci.yml` | not-inserted |
| `ci_governance.yml` | not-inserted |
| `codeql.yml` | not-inserted |
| `constitutional-audit-public.yml` | not-inserted |
| `deploy_multi.yml` | not-inserted |
| `direct_apply_fixes.yml` | not-inserted |
| `dispatch-proxy.yml` | not-inserted |
| `dispatch-workflow.yml` | parse-failed |
| `docs-suite-on-complete.yml` | not-inserted |
| `docs_suite_apply.yml` | not-inserted |
| `e2e_worker_check.yml` | not-inserted |
| `economic_snapshot.yml` | not-inserted |
| `emergency_orchestrator.yml` | not-inserted |
| `emergency_orchestrator_lite.yml` | parse-failed |
| `enqueue-test.yml` | not-inserted |
| `entities_runner.yml` | not-inserted |
| `export-hcb-weekly.yml` | not-inserted |
| `export-hcb.yml` | not-inserted |
| `finance-credential-boundary-validation.yml` | not-inserted |
| `financial_rollup.yml` | not-inserted |
| `fix-dispatch-triggers.yml` | not-inserted |
| `fix_it.yml` | not-inserted |
| `force-setup-common-python.yml` | not-inserted |
| `forward-to-bridge.yml` | not-inserted |
| `genesis_boot.yml` | not-inserted |
| `genesis_economic_snapshot.yml` | not-inserted |
| `genesis_financial_audit.yml` | not-inserted |
| `genesis_financial_telemetry.yml` | not-inserted |
| `guardian_repo_alignment.yml` | not-inserted |
| `guardian_repo_alignment_check.yml` | not-inserted |
| `guardian_repo_alignment_fixer.yml` | not-inserted |
| `guardian_worker_READMEs.yml` | not-inserted |
| `guardian_worker_workflows.yml` | not-inserted |
| `guardian_workflows.yml` | not-inserted |
| `guardians.yml` | not-inserted |
| `hcb-pipeline.yml` | not-inserted |
| `hybrid_bridge_ci.yml` | not-inserted |
| `hybrid_bridge_functional.yml` | parse-failed |
| `ingest_conversation.yml` | not-inserted |
| `ingestion-orchestrator.yml` | not-inserted |
| `install_self_healing_pack.yml` | not-inserted |
| `intent_guard.yml` | not-inserted |
| `kick-autopatch-apply.yml` | not-inserted |
| `kick-autopatch.yml` | not-inserted |
| `kick-seed-steg-config.yml` | not-inserted |
| `kick-yaml-bulk-autofix.yml` | not-inserted |
| `ledger_integrity.yml` | not-inserted |
| `log_revenue.yml` | not-inserted |
| `multi-autopatch.yml` | not-inserted |
| `neutralize_secrets_if.yml` | parse-failed |
| `nightly_snapshot.yml` | not-inserted |
| `one-shot-workflow-normalizer.yml` | not-inserted |
| `one_button_supercheck.yml` | not-inserted |
| `one_shot_patch_apply.yml` | not-inserted |
| `ops-console-dispatcher.yml` | not-inserted |
| `ops-console.yml` | not-inserted |
| `org_cleanup_autofix.yml` | not-inserted |
| `org_cleanup_worker.yml` | not-inserted |
| `pat_auditor.yml` | not-inserted |
| `pat_secrets_guardian.yml` | not-inserted |
| `patch_artifacts_index.yml` | parse-failed |
| `patch_convert_to_uploader.yml` | parse-failed |
| `patch_triggers.yml` | not-inserted |
| `patient-owned-monitoring-validation.yml` | not-inserted |
| `ping.yml` | not-inserted |
| `propagate-commit-template-v1_1.yml` | not-inserted |
| `propagate-commit-template.yml` | not-inserted |
| `propagate-readme-badges.yml` | not-inserted |
| `quickkick-sweep.yml` | not-inserted |
| `readme-nudge-kicks.yml` | not-inserted |
| `readme-nudge-yaml-autofix.yml` | not-inserted |
| `rebuild-kit.yml` | not-inserted |
| `reindex-nudge.yml` | not-inserted |
| `reindex-watchdog.yml` | parse-failed |
| `repair-bad-yaml.yml` | not-inserted |
| `repo-hygiene.yml` | not-inserted |
| `repo-timeline.yml` | not-inserted |
| `repo-tree.yml` | not-inserted |
| `repo_guardian.yml` | parse-failed |
| `repo_inventory_and_diff.yml` | not-inserted |
| `repo_snapshot_for_review.yml` | parse-failed |
| `retrofit-setup-common-python.yml` | parse-failed |
| `revenue_event_manual.yml` | not-inserted |
| `save_conversation.yml` | not-inserted |
| `scw-api-autodeploy.yml` | not-inserted |
| `scw-api-config-and-deploy.yml` | not-inserted |
| `scw-api-health-and-report.yml` | not-inserted |
| `scw_bridge.yml` | not-inserted |
| `scw_fix_no_dispatch.yml` | not-inserted |
| `scw_orchestrator.yml` | not-inserted |
| `scw_workflow_runnability_audit.yml` | not-inserted |
| `seed-autodocs-verify.yml` | not-inserted |
| `seed-steg-config.yml` | not-inserted |
| `seed_config.yml` | not-inserted |
| `self-healing-scan.yml` | not-inserted |
| `setup-common-python.yml` | not-inserted |
| `smoke-tests.yml` | not-inserted |
| `smoke_api_worker.yml` | parse-failed |
| `stegcore_governance_bootstrap.yml` | parse-failed |
| `stegtalk_writer.yml` | parse-failed |
| `stegtvc_connectivity_autopatch.yml` | not-inserted |
| `stegtvc_connectivity_sync.yml` | not-inserted |
| `stegverse-multi-autopatch.yml` | not-inserted |
| `stegverse_hypercore_selfcheck.yml` | not-inserted |
| `structure_on_demand.yml` | parse-failed |
| `supercheck_remote.yml` | not-inserted |
| `sweep_all.yml` | not-inserted |
| `taskops-export-weekly.yml` | parse-failed |
| `taskops-first-run-complete.yml` | parse-failed |
| `taskops-first-run-regression.yml` | parse-failed |
| `taskops-first-run-update.yml` | not-inserted |
| `taskops-nightly.yml` | not-inserted |
| `telemetry-reusable.yml` | not-inserted |
| `test-readiness.yml` | not-inserted |
| `token_smoke_test.yml` | not-inserted |
| `validate-autopatch-manifest.yml` | not-inserted |
| `validate-hcb.yml` | not-inserted |
| `validate-setup-common-python.yml` | not-inserted |
| `verify_ui.yml` | not-inserted |
| `weekly_drift_report.yml` | not-inserted |
| `workflow-dispatch-guardian.yml` | not-inserted |
| `workflow-recovery-controller.yml` | not-inserted |
| `workflow-status-badges.yml` | parse-failed |
| `workflow-status-check.yml` | parse-failed |
| `workflow_preflight.yml` | not-inserted |
| `workflows-badges-nudge.yml` | not-inserted |
| `workflows-badges.yml` | not-inserted |
| `workflows-console-table.yml` | not-inserted |
| `workflows-first-aid-sweep.yml` | not-inserted |
| `workflows-first-aid.yml` | not-inserted |
| `workflows-sanity-check.yml` | not-inserted |
| `workflows-second-aid.yml` | parse-failed |
| `workflows-status-badges.yml` | parse-failed |
| `yaml-bulk-autofix.yml` | not-inserted |
| `yaml_corrector.yml` | parse-failed |
| `yaml_corrector_v2.yml` | parse-failed |
<!-- pr-safe-status:end -->
