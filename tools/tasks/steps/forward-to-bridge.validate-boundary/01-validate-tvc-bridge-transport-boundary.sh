python - <<'PY'
from pathlib import Path

path = Path("tools/tasks/folded/forward-to-bridge.yml")
text = path.read_text(encoding="utf-8")
stripped = [line.strip() for line in text.splitlines() if not line.lstrip().startswith("#")]

secret_expr = "$" + "{{ " + "secrets."
gh_api = "gh " + "api"
gh_auth = "gh " + "auth"
dispatch_endpoint = "/" + "dispatches"
dispatch_event = "event_" + "type="

assert "contents: read" in stripped
assert "persist-credentials: false" in stripped
assert secret_expr not in text
assert gh_api not in text
assert gh_auth not in text
assert dispatch_endpoint not in text
assert dispatch_event not in text
assert "TVC_ADMITTED_TRANSPORT_REQUIRED" in text
print("SCW_AI_BRIDGE_HOSTED_DISPATCH_RETIRED_PASS")
PY
