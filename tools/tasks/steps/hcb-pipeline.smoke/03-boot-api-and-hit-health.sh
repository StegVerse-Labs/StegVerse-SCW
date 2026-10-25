set -e
uvicorn app.main:app --host 127.0.0.1 --port 8080 &
SV_PID=$!
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8080/health >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done
curl -fsS http://127.0.0.1:8080/health | tee /tmp/health.json
kill $SV_PID || true
