# Running the Delivery Pipeline on EC2

End-to-end guide for running `deliver.sh` on a headless EC2 instance:
**run eval → convert to harbour CLI format → push to the delivery repo.**

The pipeline lives in one script: [`deliver.sh`](./deliver.sh). It orchestrates the
existing `script/run.sh` (eval) and `script/repackage_to_bundle.py` (format conversion),
then commits + pushes the converted bundles to
[`Ethara-Ai/kensei-delievery`](https://github.com/Ethara-Ai/kensei-delievery)
under the `test_deliverables/` folder on `main`.

---

## 0. What you need before starting

| Requirement | Why | Needed for |
|---|---|---|
| **GitHub PAT** (classic, `repo` scope) | clone private repo + push to delivery repo | always |
| **git + git-lfs** | push; binaries go through LFS (on by default) | always |
| **python3 + pip** | runs the converter | always |
| **Docker (running)** + agent image | the eval runs in a container | only `--run` |
| **`.env` with API keys** | the agent calls the model | only `--run` |

> The **one** PAT covers both the private `WildClawBench` clone and the
> `kensei-delievery` push. Make sure it has access to **both** repos in the
> `Ethara-Ai` org.

---

## 1. One-time setup on the EC2 box

```bash
# --- system packages (Ubuntu/Debian AMI) ---
sudo apt-get update
sudo apt-get install -y git git-lfs python3 python3-pip
git lfs install

# --- Docker (only needed if you will use --run) ---
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"      # log out/in once so docker works without sudo
```

> Amazon Linux 2023 instead of Ubuntu? Use:
> `sudo dnf install -y git git-lfs python3 python3-pip docker && sudo systemctl enable --now docker`

---

## 2. Set your PAT (every shell session)

```bash
export GITHUB_TOKEN=ghp_your_real_token
```

- Do **not** bake the token into a script or AMI. Set it at run time, or pull it
  from AWS Secrets Manager / SSM Parameter Store.
- `deliver.sh` reads `GITHUB_TOKEN` (or `GH_TOKEN`) and authenticates the delivery
  push non-interactively — no username/password prompt.

---

## 3. Clone this repo (private-repo safe)

```bash
# clone WildClawBench using the PAT (works whether public or private)
git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/Ethara-Ai/WildClawBench.git"
cd WildClawBench

# strip the token back out of origin (hygiene — keeps it out of .git/config)
git remote set-url origin https://github.com/Ethara-Ai/WildClawBench.git

# python deps
pip3 install -r requirements.txt
```

---

## 4. Configure `.env` (only if using `--run`)

```bash
cp .env.example .env
nano .env            # fill in the API keys the agent needs
```

Also make sure the **agent Docker image** `run.sh` expects is available on the box
(loaded from `Images/*.tar` or however you normally provision it). If it's missing,
`run.sh` preflight will fail loudly before any work happens.

---

## 5. Run the pipeline

> Long runs: wrap in `tmux` so an SSH disconnect doesn't kill the job.
> `tmux new -s deliver` … run … detach with `Ctrl-b d`, reattach with `tmux attach -t deliver`.

### A. Full pipeline — run eval, convert, push (the common case)

```bash
export GITHUB_TOKEN=ghp_your_real_token

./deliver.sh --run \
  --task input/ben_cox_8fc24d4b-dd01-44db-95b5-98d0b7786af5 \
  --task input/chris_murray_d0b75eea-81b2-4fbc-8e0d-57c16e39954d
```

This runs both tasks in Docker → converts to harbour CLI format → LFS-tracks
binaries → pushes into `test_deliverables/` on `main`.

### B. Test first — everything EXCEPT the push

```bash
./deliver.sh --run --dry-run \
  --task input/ben_cox_8fc24d4b-dd01-44db-95b5-98d0b7786af5 \
  --task input/chris_murray_d0b75eea-81b2-4fbc-8e0d-57c16e39954d
```

### C. Convert + push EXISTING output only (no eval, no Docker, no `.env`)

```bash
export GITHUB_TOKEN=ghp_your_real_token
./deliver.sh                          # all existing output  -> test_deliverables/
./deliver.sh --persona "ben cox"      # just one existing task
```

---

## 6. Command reference (`deliver.sh`)

| Flag | Meaning |
|---|---|
| `--run` | run the eval first (needs Docker + `.env`); otherwise convert existing output |
| `--task <path>` | a task to run; repeat for several |
| `--all-tasks` | run every task under `input/` |
| `--tasks-file <file>` | run a list of tasks (one path per line) |
| `--persona "<name>"` | convert-only mode: package one existing task by fuzzy name |
| `--model <m>` / `-k <N>` | override run.sh model / number of runs (default: `claude-opus-4.7`, K=1) |
| `--deliverable <dir>` | target folder in the delivery repo (default: `test_deliverables`) |
| `--branch <name>` | delivery branch (default: `main`) |
| `--no-lfs` | disable Git LFS (default: LFS on) |
| `--dry-run` | do everything except the final push |
| `-h`, `--help` | full help |

Run `./deliver.sh --help` for the authoritative list.

---

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `clone failed` / hangs | `GITHUB_TOKEN` not set or lacks access. Re-export it; confirm PAT `repo` scope covers both repos. |
| `push failed` | PAT can read but not write the delivery repo. Check write access / org SSO authorization on the PAT. |
| `git-lfs not installed` warning | Install git-lfs (`sudo apt-get install -y git-lfs && git lfs install`) or pass `--no-lfs`. |
| `run.sh` preflight error | Docker not running or agent image missing. Start Docker; load the image. |
| Model/auth errors during `--run` | `.env` keys missing/invalid. |
| SSH dropped mid-run | Use `tmux`/`nohup`; reattach after reconnecting. |

---

## 8. Quick copy-paste (private repo, full pipeline)

```bash
# one-time
sudo apt-get update && sudo apt-get install -y git git-lfs python3 python3-pip docker.io
git lfs install && sudo systemctl enable --now docker && sudo usermod -aG docker "$USER"

# each session
export GITHUB_TOKEN=ghp_your_real_token
git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/Ethara-Ai/WildClawBench.git"
cd WildClawBench
git remote set-url origin https://github.com/Ethara-Ai/WildClawBench.git
pip3 install -r requirements.txt
cp .env.example .env && nano .env        # add API keys

./deliver.sh --run \
  --task input/ben_cox_8fc24d4b-dd01-44db-95b5-98d0b7786af5 \
  --task input/chris_murray_d0b75eea-81b2-4fbc-8e0d-57c16e39954d
```
