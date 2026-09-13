#!/usr/bin/env bash
# M0 acceptance gate for the WildClawBench dsh harness image.
set -euo pipefail
cd "$(dirname "$0")/.."
docker build -f docker/Dockerfile.dsh -t wildclawbench-dsh:v0.1 .
cid=$(docker run -d --rm wildclawbench-dsh:v0.1 tail -f /dev/null)
trap 'docker rm -f "$cid" >/dev/null 2>&1 || true' EXIT
docker exec "$cid" dsh --version | grep -q 0.1.5
docker exec "$cid" dsh --profile bench --dump-config | grep -q "reasoningEffort: xhigh"
docker exec "$cid" dsh --profile bench --dump-config | grep -q "model: qwen3.8-flash-next"
docker exec "$cid" /bin/bash -c \
  'curl -sf -m 10 http://100.64.0.1:4000/v1/models | grep -q qwen3.8-flash-next \
   || curl -sf -m 10 http://host.docker.internal:4000/v1/models | grep -q qwen3.8-flash-next'
docker exec "$cid" /bin/bash -c \
  'cd /tmp && dsh --profile bench "reply with exactly: OK"' | grep -q OK
echo "IMAGE OK"
