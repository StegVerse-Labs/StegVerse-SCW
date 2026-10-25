set -euo pipefail
mkdir -p .github/autopatch_out
git diff -- .github/workflows > .github/autopatch_out/FIRST_AID_PROPOSED.patch || true
test -f .github/autopatch_out/FIRST_AID_SUMMARY.json
