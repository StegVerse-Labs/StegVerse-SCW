# 🟢 One-Button Supercheck — Trigger Folder

This folder lets you **run and control** the `one_button_supercheck.yml` workflow
without needing to use the GitHub Actions UI manually.  
Just commit a tiny file here — the workflow starts automatically.

---

## 📂 Supported Trigger Files

| File name / pattern            | Type        | Effect |
|--------------------------------|------------|--------|
| `run-*.txt`                    | presence   | **Required** — any file in this folder starts the workflow when pushed. Name can be anything (timestamp recommended). |
| `apply.txt`                    | presence   | Forces `auto_apply=true` — applies repo triage (scaffolding, ATTIC moves, forbidden file removals). |
| `commit.txt`                   | presence   | Forces `auto_commit=true` — commits directly to `main` instead of opening PR. |
| `no-autofix.txt`               | presence   | Runs preflight but disables workflow YAML auto-fixing (dry-run only). |
| `preflight-only.txt`           | presence   | Runs only preflight (validate/fix workflows), then stops. |
| `triage-only.txt`              | presence   | Skips preflight/diagnostics — runs repo audit + triage only. |
| `skip-diag.txt`                | presence   | Skips runtime API/worker diagnostics. |
| `fast.txt`                     | presence   | Use shorter timeouts/polling (30s / 2s). |
| `deep.txt`                     | presence   | Use extended timeouts/polling (180s / 4s). |
| `attic-off.txt`                | presence   | Disable moving files to ATTIC (scaffold + remove only). |
| `diag-url.txt`                 | content    | First line overrides API base URL (e.g. ``). |
| `queue.txt`                    | content    | First line overrides worker queue key (default: `queue:runs`). |
| `timeout.txt`                  | content    | First line sets timeout in seconds (overrides default). |
| `poll.txt`                     | content    | First line sets poll interval in seconds (overrides default). |

---

## 🛠️ Example Recipes

### ✅ Run default Supercheck
```bash
echo "trigger" > .github/trigger/supercheck/run-$(date +%s).txt
git add . && git commit -m "trigger supercheck" && git push
