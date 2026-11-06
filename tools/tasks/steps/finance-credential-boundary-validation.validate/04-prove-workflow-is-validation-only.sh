python - <<'PY'
from pathlib import Path
lines = Path("tools/tasks/folded/finance-credential-boundary-validation.yml").read_text().splitlines()
stripped = [line.strip() for line in lines]
assert "contents: read" in stripped
assert "persist-credentials: false" in stripped
assert "contents: write" not in stripped
assert not any(line.startswith("uses: actions/upload-artifact@") for line in stripped)
assert not any(line.startswith(("git push", "git commit", "git tag")) for line in stripped)
print("SCW_FINANCE_CREDENTIAL_BOUNDARY_VALIDATION_ONLY_PASS")
PY
