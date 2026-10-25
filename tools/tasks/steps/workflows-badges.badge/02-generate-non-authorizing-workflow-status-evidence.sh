set -euo pipefail
mkdir -p workflow-status-evidence
python - <<'PY'
import json
import pathlib
import yaml

root = pathlib.Path(".github/workflows")
records = []
for path in sorted(root.glob("*.yml")) + sorted(root.glob("*.yaml")):
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        doc = yaml.safe_load(text)
        valid = isinstance(doc, dict)
        error = None if valid else "invalid_workflow_shape"
    except Exception as exc:
        valid = False
        error = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
    records.append({"path": path.as_posix(), "valid": valid, "error": error})

summary = {
    "total": len(records),
    "valid": sum(item["valid"] for item in records),
    "invalid": sum(not item["valid"] for item in records),
    "authority_effect": "NONE",
    "github_runtime_authority": "VALIDATION_EVIDENCE_ONLY",
}
out = {"summary": summary, "records": records}
pathlib.Path("workflow-status-evidence/workflows-status.json").write_text(
    json.dumps(out, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2))
PY
