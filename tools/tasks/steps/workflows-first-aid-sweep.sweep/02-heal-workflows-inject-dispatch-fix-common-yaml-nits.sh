set -euo pipefail
python - <<'PY'
import re, pathlib, yaml, json

ROOT   = pathlib.Path(".")
WF_DIR = ROOT / ".github" / "workflows"
OUTDIR = ROOT / ".github" / "autopatch_out"
OUTDIR.mkdir(parents=True, exist_ok=True)

def load_text(p): return p.read_text(encoding="utf-8", errors="ignore")
def save_text(p,s): p.write_text(s, encoding="utf-8")

def parse_yaml(text):
  try:
    return yaml.safe_load(text), None
  except Exception as e:
    return None, e

def has_workflow_call_only(on):
  return isinstance(on, dict) and set(on.keys()) == {"workflow_call"}

def ensure_dispatch(model):
  if not isinstance(model, dict): return False
  on = model.get("on")
  if on is None:
    model["on"] = {"workflow_dispatch": {}}
    return True
  if isinstance(on, str):
    model["on"] = {on: {}}
    on = model["on"]
  if isinstance(on, list):
    model["on"] = {k: {} for k in on if isinstance(k, str)}
    on = model["on"]
  if has_workflow_call_only(on):
    return False
  if "workflow_dispatch" not in on:
    on["workflow_dispatch"] = {}
    return True
  return False

def normalize_inline_env(lines):
  out = []
  for line in lines:
    m = re.match(r'^(\s*)env:\s*\{\s*([^}]+)\s*\}\s*$', line)
    if m:
      base = m.group(1)
      inner = m.group(2)
      out.append(f"{base}env:\n")
      for part in inner.split(","):
        part = part.strip()
        if not part: continue
        if ":" in part:
          k,v = part.split(":",1)
          out.append(f"{base}  {k.strip()}: {v.strip()}\n")
    else:
      out.append(line)
  return out

def looks_like_step_start(line):
  return bool(re.match(r'^\s*-\s+name:\s', line))

SCRIPT_LEADERS = (
  "import ","from ","set -e","set -eu","set -euo pipefail",
  "#!/usr/bin/env","python ","bash ","sh ","node ",
  "ROOT=","SHA=","git ","curl ","jq ","ts=","echo ","{","}","if [","fi"
)

def is_scriptish(line):
  s = line.lstrip()
  return any(s.startswith(t) for t in SCRIPT_LEADERS)

def indent_of(line): return len(line) - len(line.lstrip(' '))

def needs_run_insertion(lines, i):
  if lines[i].lstrip().startswith("#"): return False
  for j in range(i-1, max(-1, i-30), -1):
    t = lines[j].strip()
    if not t: continue
    if re.match(r'^\s*run\s*:\s*(\||>|\S)?', t): return False
    if looks_like_step_start(lines[j]): return True
    if re.match(r'^\S', lines[j]): return True
  return True

def inject_run_block(lines, i):
  insert_at = i
  ins_indent = max(2, indent_of(lines[i]))
  for j in range(i-1, max(-1, i-50), -1):
    if looks_like_step_start(lines[j]):
      insert_at = j+1
      ins_indent = indent_of(lines[j]) + 2
      break
    if lines[j].strip().startswith("steps:"):
      insert_at = j+1
      ins_indent = indent_of(lines[j]) + 2
      break
  lines.insert(insert_at, " " * ins_indent + "run: |\n")
  k = insert_at + 1
  while k < len(lines):
    if looks_like_step_start(lines[k]) or re.match(r'^\S', lines[k]): break
    if lines[k].strip() and not lines[k].lstrip().startswith("#"):
      lines[k] = " " * (ins_indent + 2) + lines[k].lstrip(" ")
    k += 1

fixed, added_dispatch, still_broken = [], [], []

for p in sorted(WF_DIR.glob("*.y*ml")):
  text0 = load_text(p)
  data, exc = parse_yaml(text0)

  changed_model = False
  changed_text  = False

  if exc is None:
    if ensure_dispatch(data):
      changed_model = True

  lines = text0.splitlines(keepends=True)
  n1 = normalize_inline_env(lines)
  if n1 != lines:
    lines = n1
    changed_text = True

  for idx, line in enumerate(list(lines)):
    if is_scriptish(line) and needs_run_insertion(lines, idx):
      try:
        inject_run_block(lines, idx)
        changed_text = True
      except Exception:
        pass

  if changed_model:
    try:
      cur_model = yaml.safe_load("".join(lines))
    except Exception:
      cur_model = data
    if isinstance(cur_model, dict) and isinstance(data, dict):
      cur_model["on"] = data.get("on", cur_model.get("on"))
      text_dump = yaml.safe_dump(cur_model, sort_keys=False, allow_unicode=True)
    else:
      text_dump = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    save_text(p, text_dump)
    added_dispatch.append(p.name)
    text_now = text_dump
  else:
    text_now = "".join(lines)

  if changed_text and not changed_model:
    save_text(p, text_now)

  _, new_exc = parse_yaml(load_text(p))
  if new_exc is None:
    if changed_text or changed_model:
      fixed.append(p.name)
  else:
    still_broken.append((p.name, type(new_exc).__name__))

summary = {
  "fixed": fixed,
  "added_dispatch": added_dispatch,
  "still_broken": still_broken
}
(OUTDIR / "FIRST_AID_SUMMARY.json").write_text(
  json.dumps(summary, indent=2), encoding="utf-8"
)
PY
