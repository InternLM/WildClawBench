#!/usr/bin/env bash
# M0 acceptance gate for the WildClawBench dsh harness image.
# Note: capture then grep (never `docker exec ... | grep -q` under pipefail —
# grep's early exit SIGPIPEs docker exec and trips pipefail).
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; [ -f .env ] && . ./.env; set +a
: "${WCB_LB_API_KEY:?WCB_LB_API_KEY required in .env}"

docker build -f docker/Dockerfile.dsh -t wildclawbench-dsh:v0.1 .
cid=$(docker run -d --rm -e WCB_LB_API_KEY="$WCB_LB_API_KEY" \
      wildclawbench-dsh:v0.1 tail -f /dev/null)
trap 'docker rm -f "$cid" >/dev/null 2>&1 || true' EXIT

ver=$(docker exec "$cid" dsh --version)
echo "$ver" | grep -q 0.1.5 || { echo "FAIL: dsh version '$ver'"; exit 1; }

dump=$(docker exec "$cid" dsh --profile bench --dump-config 2>/dev/null)
echo "$dump" | grep -q "reasoningEffort: xhigh" || { echo "FAIL: rung not xhigh"; exit 1; }
echo "$dump" | grep -q "model: qwen3.8-flash-next" || { echo "FAIL: model not pinned"; exit 1; }
echo "$dump" | grep -q "provider: wcb-lb" || { echo "FAIL: provider not wcb-lb"; exit 1; }

models=$(docker exec "$cid" /bin/bash -c \
  "curl -s -m 10 -H \"Authorization: Bearer \$WCB_LB_API_KEY\" http://100.64.0.1:4000/v1/models")
echo "$models" | grep -q qwen3.8-flash-next || { echo "FAIL: LB not serving model"; exit 1; }

ok=$(docker exec "$cid" /bin/bash -c \
  'cd /tmp && dsh --profile bench "reply with exactly: OK" 2>/dev/null')
echo "$ok" | grep -q OK || { echo "FAIL: live LLM round-trip"; exit 1; }

echo "IMAGE OK"
