set -euo pipefail
python - <<'PY'
import yaml, pathlib, datetime

ROOT   = pathlib.Path(".")
WF_DIR = ROOT/".github/workflows"
DOC    = ROOT/".github/docs/WORKFLOWS_CONSOLE.md"
DOC.parent.mkdir(parents=True, exist_ok=True)

def load_yaml(p):
  try:
    return yaml.safe_load(p.read_text(encoding="utf-8"))
  except Exception as e:
    return e

def has_dispatch(d):
  if not isinstance(d, dict): return False
  on = d.get("on")
  if on is None: return False
  if isinstance(on, str): return on == "workflow_dispatch"
  if isinstance(on, list): return "workflow_dispatch" in on
  if isinstance(on, dict):
    return ("workflow_dispatch" in on) and (set(on.keys()) != {"workflow_call"})
  return False

rows, ok, nodisp, broken = [], 0, 0, 0
for p in sorted(WF_DIR.glob("*.y*ml")):
  data = load_yaml(p)
  if isinstance(data, Exception):
    broken += 1
    state = f"❌ broken · `{type(data).__name__}`"
  else:
    if has_dispatch(data):
      ok += 1
      state = "✅ ok"
    else:
      nodisp += 1
      state = "➖ no-dispatch"
  gh = "https://github.com/StegVerse/StegVerse-SCW/actions/workflows/" + p.name
  rows.append(f"| `{p.name}` | {state} | [Run]({gh}) · [View]({gh}) · [File](.github/workflows/{p.name}) |")

total = ok + nodisp + broken
now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

lines = []
lines += [ "# Ops Console", "", f"_Last updated: **{now}**_", "", f"- ✅ OK: **{ok}**", f"- ➖ No dispatch: **{nodisp}**", f"- ❌ Broken: **{broken}**", f"- Total: **{total}**", "", "| Workflow | State | Actions |", "|---|---|---|" ]
lines += rows
DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
