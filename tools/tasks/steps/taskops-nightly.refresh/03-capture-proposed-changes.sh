set -euo pipefail
git diff -- README.md .github/docs/ > taskops-proposed.patch
if [ -s taskops-proposed.patch ]; then
  echo "TaskOps generated proposed documentation changes; publication is not authorized here."
else
  echo "TaskOps generated no documentation delta."
fi
