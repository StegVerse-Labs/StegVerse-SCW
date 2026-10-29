set -euo pipefail
mkdir -p out
if [ -d ".github/trigger" ]; then
  tar -czf out/trigger.tgz .github/trigger
else
  echo "No .github/trigger directory in source."
  mkdir -p .github/trigger
  tar -czf out/trigger.tgz .github/trigger
fi

jq -n \
  --arg repo "${{ github.repository }}" \
  --arg sha "${{ github.sha }}" \
  --arg run_id "${{ github.run_id }}" \
  --arg event "${{ github.event_name }}" \
  --arg time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{
    schema:"stegverse.scw.trigger-backup-evidence/v1",
    source:$repo,
    source_sha:$sha,
    workflow_run_id:$run_id,
    event:$event,
    generated_at:$time,
    authority_effect:"NONE_VALIDATION_EVIDENCE_ONLY",
    external_repository_mutation:false,
    publication:false
  }' > out/manifest.json
