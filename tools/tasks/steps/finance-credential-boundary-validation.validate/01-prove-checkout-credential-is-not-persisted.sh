set -euo pipefail
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
test -z "$(git config --local --get http.https://github.com/.extraheader || true)"
test -z "$(git config --local --get-all credential.helper || true)"
