#!/usr/bin/env bash
# ec2_bootstrap.sh — one-shot setup + injection smoke-test for WildClawBench on
# a fresh x86_64 Amazon Linux EC2 instance.
#
#   bash script/ec2_bootstrap.sh            # install deps, load image, run check_injection ($0)
#   bash script/ec2_bootstrap.sh --run      # ...then also launch the full LAYLA task (~80 min, billable)
#
# Idempotent: re-running skips anything already done.
set -uo pipefail
TASK="input/LAYLA_001_october_grant_crunch"
MODEL="claude-opus-4.7"
RUN_FULL=0; [[ "${1:-}" == "--run" ]] && RUN_FULL=1
step(){ printf '\n\033[1;36m== %s ==\033[0m\n' "$1"; }
die(){ printf '\033[1;31mFATAL: %s\033[0m\n' "$1"; exit 1; }

step "0. sanity"
[[ "$(uname -m)" == "x86_64" ]] || echo "WARNING: arch=$(uname -m); agent image is linux/amd64 — expect emulation/failures on arm64"
[[ -f run.sh ]] || die "run from the repo root (run.sh not found)"
[[ -f .env ]] || echo "WARNING: .env missing — copy your credentials file here before the full run (--run will fail without Bedrock creds)"

step "1. packages (docker, git, python3, pip)"
PKG=$(command -v dnf || command -v yum)
sudo "$PKG" install -y docker git python3 python3-pip >/dev/null 2>&1 || die "package install failed"
sudo systemctl enable --now docker >/dev/null 2>&1 || die "could not start docker"
if ! docker ps >/dev/null 2>&1; then
  sudo usermod -aG docker "$USER" || true
  echo "Added $USER to docker group. Using 'sudo docker' for this run; log out/in to use docker without sudo."
  DOCKER="sudo docker"
else
  DOCKER="docker"
fi
echo "docker: $($DOCKER --version)"

step "2. python deps"
python3 -m pip install -q --user -r requirements.txt || die "pip install failed"

step "3. agent image wildclawbench-ubuntu:v1.3 (linux/amd64, ~28GB)"
if $DOCKER image inspect wildclawbench-ubuntu:v1.3 >/dev/null 2>&1; then
  echo "image already loaded — skipping"
else
  if [[ ! -f Images/wildclawbench-ubuntu_v1.3.tar ]]; then
    echo "fetching image tar from HuggingFace..."
    python3 -m pip install -q --user "huggingface_hub[cli]"
    mkdir -p Images
    hf download internlm/WildClawBench Images/wildclawbench-ubuntu_v1.3.tar \
        --repo-type dataset --local-dir . \
      || die "HF download failed. If gated, copy the tar from your Mac instead:
   docker save wildclawbench-ubuntu:v1.3 | gzip | ssh -i talos.pem ec2-user@<ip> 'gunzip | docker load'"
  fi
  echo "loading image (2-15 min)..."
  $DOCKER load -i Images/wildclawbench-ubuntu_v1.3.tar || die "docker load failed"
fi

step "4. injection smoke-test (free, ~1 min, no model calls)"
python3 script/check_injection.py "$TASK" || die "check_injection failed — stop and inspect before spending on a full run"

if [[ "$RUN_FULL" -eq 1 ]]; then
  step "5. FULL RUN ($MODEL, ~80 min, billable)"
  ./run.sh "$TASK" "$MODEL" 1
else
  step "DONE — setup + injection check passed"
  echo "Launch the full task with:   ./run.sh $TASK $MODEL 1"
  echo "(use tmux so it survives an SSH drop)"
fi
