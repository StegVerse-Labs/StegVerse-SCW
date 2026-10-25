set -e
echo "Using providers path: ${HCB_PROVIDERS_PATH}"
uvicorn app.main:app --host 127.0.0.1 --port 8080 &
SV_PID=$!
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8080/health >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done
echo '>>> /health'
curl -fsS http://127.0.0.1:8080/health | tee /tmp/health.json
echo '>>> /v1/run'
curl -fsS -X POST http://127.0.0.1:8080/v1/run \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-TOKEN: ${ADMIN_TOKEN}" \
  -d '{"slug":"ci-functional","question":"Give a one-line project summary.","context":"HCB functional test","experts":["claude"],"strategy":"consensus","human_gate":true,"temperature":0.1}' \
  | tee /tmp/run.json
kill $SV_PID || true
