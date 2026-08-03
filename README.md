<h1 align="center">WildClawBench</h1>

<p align="center">
  <img src="assets/lobster_battle.png" alt="WildClawBench Lobster" width="480">
</p>

<div align="center">


[![Tasks](https://img.shields.io/badge/Tasks-60-blue)]()
[![Harnesses](https://img.shields.io/badge/Harnesses-4-purple)]()
[![Models](https://img.shields.io/badge/Models-26-green)]()
[![Leaderboard](https://img.shields.io/badge/🏆_Leaderboard-WildClawBench-8c2416)](https://internlm.github.io/WildClawBench/)
<br>
[![arXiv](https://img.shields.io/badge/arXiv-2605.10912-b31b1b.svg)](https://arxiv.org/abs/2605.10912)
[![HF Daily Paper](https://img.shields.io/badge/🤗_Daily_Paper-Featured-ffcc00)](https://huggingface.co/papers/2605.10912)
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-Dataset-yellow)](https://huggingface.co/datasets/internlm/WildClawBench)
[![PDF Report](https://img.shields.io/badge/📄_Paper-PDF-red)](https://github.com/InternLM/WildClawBench/blob/main/WildClawBench_report.pdf)

</div>


> **Hard, practical, end-to-end evaluation for AI agents — in the wild.**

---

**WildClawBench** is an agent benchmark that tests what actually matters: can an AI agent do real work, end-to-end, without hand-holding?

We drop agents into a live [OpenClaw](https://github.com/openclaw/openclaw) environment — the same open-source personal AI assistant that real users rely on daily — and throw **60 original tasks** at them: clipping goal highlights from a football match, negotiating meeting times over multi-round emails, hunting down contradictions in search results, writing inference scripts for undocumented codebases, catching privacy leaks before they happen. Useful things. Hard things.

In the **technical report snapshot**, the strongest frontier model topped out at **62.2% overall**; the latest audited OpenClaw runs have since raised the best score to **67.2%**. Most models still land well below that. That makes scores mean something.

### Why WildClawBench?

Most agent benchmarks test isolated capabilities — calling a function, parsing JSON, following a single instruction. WildClawBench tests the full picture:

| | What We Test | Why It's Hard |
|:---:|---|---|
| **🔗 Agency** | Multi-step tool orchestration, error recovery, autonomous planning | Agents must chain 10–60+ tool calls, adapt when services fail, and decide *what* to do — not just *how* |
| **🎥 Multimodal** | Video understanding, image generation, cross-modal synthesis | Track events across a 45-min match video and clip precise highlights; classify 12 clothing photos, assemble 4 styled outfits, and generate full-body model images for each |
| **🧵 Long-Horizon** | Complex workflows spanning 10–20 minutes of wall-clock execution | Negotiate meeting times over multiple email rounds; crawl, classify, and summarize 50+ academic papers |
| **💻 Coding** | Read undocumented codebases, debug, generate working programs | Read an undocumented codebase, install dependencies, and write working inference from source alone; solve visual puzzles by generating pixel-accurate solutions |
| **🛡️ Safety** | Prompt injection defense, credential leak detection, harmful content refusal | Harmful instructions are buried deep inside normal-looking documents; API keys are scattered across a large git history |

### What Sets Us Apart

- **Real environment, not mocks.** Tasks run inside a live OpenClaw instance with real tools (browser, bash, file system, email, calendar).
- **60 original tasks, built by hand.** Not adapted from existing benchmarks — each task was designed from scratch to stress-test real-world agent capabilities.
- **Four agent harnesses, one task suite.** OpenClaw, Claude Code, Codex CLI, and Hermes Agent all execute the same 60 tasks under the same grading. This separates *model capability* from *harness scaffolding* — you can see how much an agent's score depends on its surrounding tools versus the underlying LLM.
- **Reproducible & isolated.** Each task runs in its own Docker container. Same image, same data, same grading code. Ground truth and grading scripts are injected only after the agent finishes — they are never visible during execution, eliminating data leakage. Scores are reproducible across machines.

## News

- **2026-07** We expanded the OpenClaw leaderboard with evaluations of the latest frontier models, including **GPT-5.6 Sol, Claude Fable 5, Kimi K3 and etc**.
- **2026-06** ByteDance Seed's **[Seed2.1 release](https://seed.bytedance.com/en/blog/seed2-1-officially-released-advancing-ai-productivity)** includes WildClawBench in its agent evaluations. Thanks for the recognition!
- **2026-05** We released a new version with **four agent harnesses** — OpenClaw, Claude Code, Codex CLI, and Hermes Agent — so the same 60-task suite can be evaluated under multiple scaffolds.
- **2026-05** We published a **[technical report PDF](WildClawBench_report.pdf)**.
- **2026-05** Tencent’s **[Hunyuan3 Preview](https://hunyuan.tencent.com/research/hy3)** page reports WildClawBench evaluation scores. Thanks for the recognition!

---

## Leaderboard

WildClawBench reports two complementary leaderboards:

1. **Model leaderboard (OpenClaw harness)** — apples-to-apples comparison of LLMs running inside the same OpenClaw harness.
2. **Harness comparison** — same model, same tasks, four different agent scaffolds.

Full interactive leaderboard at [internlm.github.io/WildClawBench](https://internlm.github.io/WildClawBench/).

### Model leaderboard (OpenClaw harness)

> **Overall score** follows the weighted Multimodal / Pure-text breakdown in that table. **Total time** and **total cost** are the paper’s Overall per-task averages (minutes / USD) multiplied by **60** for the full 60-task suite.


| Rank | Model | Org | Overall Score | Total Time | Total Cost |
|:----:|-------|-----|:-------------:|:----------:|:----------:|
| 🥇 | **GPT-5.6 Sol** | OpenAI | **67.2%** | 222 min | $56.78 |
| 🥈 | Claude Opus 4.8 | Anthropic | 64.7% | 400 min | $95.95 |
| 🥉 | Claude Opus 4.7 | Anthropic | 62.2% | 328 min | $77.40 |
| 4 | Claude Fable 5 | Anthropic | 62.0% | 324 min | $87.71 |
| 5 | GPT-5.5 | OpenAI | 58.2% | 262 min | $37.80 |
| 6 | Grok 4.5 | xAI | 57.5% | 359 min | $28.43 |
| 7 | Muse Spark 1.1 | Meta | 54.8% | 367 min | $23.59 |
| 8 | Kimi K3 | Moonshot AI | 54.5% | 488 min | $40.08 |
| 9 | GLM 5.2 | Zhipu AI | 54.2% | 442 min | $17.10 |
| 10 | Claude Opus 4.6 | Anthropic | 51.6% | 508 min | $81.00 |
| 11 | GPT-5.4 | OpenAI | 50.3% | 350 min | $19.80 |
| 12 | Hy3 | Tencent | 49.7% | 338 min | $2.13 |
| 13 | GLM 5.1 | Zhipu AI | 48.2% | 515 min | $34.80 |
| 14 | DeepSeek V4 Pro | DeepSeek | 43.7% | 605 min | $12.00 |
| 15 | MiMo V2.5 Pro | Xiaomi | 43.0% | 451 min | $12.60 |
| 16 | GLM 5 | Zhipu AI | 42.6% | 373 min | $11.40 |
| 17 | Gemini 3.1 Pro | Google DeepMind | 40.8% | 240 min | $18.00 |
| 18 | MiMo V2 Pro | Xiaomi | 40.2% | 458 min | $26.40 |
| 19 | Qwen3.5 397B | Alibaba Cloud | 34.5% | 459 min | $22.20 |
| 20 | DeepSeek V3.2 | DeepSeek | 34.0% | 549 min | $11.40 |
| 21 | GLM 5 Turbo | Zhipu AI | 33.9% | 499 min | $15.00 |
| 22 | MiniMax M2.7 | MiniMax | 33.8% | 551 min | $7.20 |
| 23 | Kimi K2.5 | Moonshot AI | 30.8% | 406 min | $6.60 |
| 24 | MiMo V2 Flash | Xiaomi | 30.8% | 433 min | $10.20 |
| 25 | MiniMax M2.5 | MiniMax | 27.1% | 542 min | $9.60 |
| 26 | Step 3.5 Flash | StepFun | 26.7% | 430 min | $6.60 |
| 27 | Grok 4.20 Beta | xAI | 19.3% | 94 min | $9.60 |

> Claude Opus 4.8 cost uses the dynamic base-tier rates for this evaluation: $5/M input, $25/M output, $0.5/M cache read, and $6.25/M cache write.

### Harness comparison

Same 60 tasks, same grading, four different agent scaffolds. Time and cost are per-task averages; score is in %. Time is in minutes per task, cost in USD per task. **Bold** = best harness for that model.

| Model | OpenClaw |  |  | Claude Code |  |  | Codex |  |  | Hermes Agent |  |  |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|  | Time | Cost | Score | Time | Cost | Score | Time | Cost | Score | Time | Cost | Score |
| GPT-5.4      | 5.83 | $0.33 | 50.3 | 9.07 | $0.61 | 48.4 | 7.16 | $0.57 | **56.8** | 8.97 | $0.44 | 50.7 |
| GLM 5        | 6.22 | $0.19 | 42.6 | 10.18 | $0.21 | 31.0 | 7.84 | $0.13 | 38.9 | 6.62 | $0.44 | **46.4** |
| MiMo V2 Pro  | 7.63 | $0.44 | 40.2 | 9.90 | $0.15 | 29.9 | 6.44 | $0.15 | 35.3 | 8.30 | $0.26 | **48.1** |
| MiniMax M2.7 | 9.18 | $0.12 | 33.8 | 10.08 | $0.09 | 32.0 | 8.66 | $0.06 | 35.8 | 10.30 | $0.11 | **37.1** |


---

## Tasks

**60 tasks** across **6 categories**, spanning English and Chinese:

| Category | # | Example Tasks | Core Challenges |
|:---------|:-:|---------------|-----------------|
| **Productivity Flow** | 10 | ArXiv paper digest, PDF batch classification, calendar scheduling, Wikipedia biography, LaTeX table extraction | Information synthesis, multi-source aggregation, structured output |
| **Code Intelligence** | 12 | SAM3 inference from source, visual puzzle solving (jigsaw, connect-the-dots, link-a-pix), benchmark reproduction, academic homepage generation | Undocumented codebase comprehension, pixel-level visual reasoning, end-to-end code generation |
| **Social Interaction** | 6 | Multi-round meeting negotiation, chat action extraction, escalation routing, cross-department updates | Multi-turn communication, API orchestration, context tracking |
| **Search & Retrieval** | 11 | Conflicting information resolution, financial data extraction, fuzzy repository search | Web search + local data reconciliation, multi-constraint satisfaction, source verification |
| **Creative Synthesis** | 11 | Football match report with video clips, video English-to-Chinese dubbing, paper-to-poster, product launch video analysis, outfit-to-model image | Video/audio processing, cross-modal generation, design & layout |
| **Safety Alignment** | 10 | Prompt injection via file content, leaked API key detection, malicious skill injection, misinformation refusal, file overwrite prevention | Adversarial robustness, credential awareness, harmful content refusal |

To create new tasks, see the annotated template at [`tasks/task0_template.md`](tasks/task0_template.md).

## Quick Start

### Install Docker

<details>
<summary>macOS</summary>

```bash
brew install --cask docker
```

After installation, launch Docker Desktop from Applications or run:

```bash
open -a Docker
```

</details>

<details>
<summary>Ubuntu</summary>

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add apt repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Allow current user to run Docker without sudo
sudo usermod -aG docker $USER
newgrp docker
```

</details>

### Download Images

WildClawBench ships **four** Docker images, one per harness. They are all hosted on [HuggingFace](https://huggingface.co/datasets/internlm/WildClawBench/tree/main/Images). Pick the one(s) that match the harness you want to evaluate:

| Harness | Image tarball | Loaded tag |
|---|---|---|
| OpenClaw     | `wildclawbench-ubuntu_v1.3.tar`                       | `wildclawbench-ubuntu:v1.3` |
| Claude Code  | `wildclawbench-claudecode-ubuntu_v0.2-patched.tar`    | `wildclawbench-claudecode-ubuntu:v0.2` |
| Codex CLI    | `wildclawbench-codex-ubuntu_v0.0.tar`                 | `wildclawbench-codex-ubuntu:v0.0` |
| Hermes Agent | `wildclawbench-hermes-agent-v0.5.tar.gz`              | `wildclawbench-hermes-agent:v0.5` |

```bash
pip install -U "huggingface_hub[cli]"

# Download the images you need (or all four)
hf download internlm/WildClawBench Images/wildclawbench-ubuntu_v1.3.tar                    --repo-type dataset --local-dir .
hf download internlm/WildClawBench Images/wildclawbench-claudecode-ubuntu_v0.2-patched.tar --repo-type dataset --local-dir .
hf download internlm/WildClawBench Images/wildclawbench-codex-ubuntu_v0.0.tar              --repo-type dataset --local-dir .
hf download internlm/WildClawBench Images/wildclawbench-hermes-agent-v0.5.tar.gz           --repo-type dataset --local-dir .
```

Then load each image into Docker:

```bash
docker load -i Images/wildclawbench-ubuntu_v1.3.tar
docker load -i Images/wildclawbench-claudecode-ubuntu_v0.2-patched.tar
docker load -i Images/wildclawbench-codex-ubuntu_v0.0.tar
docker load -i Images/wildclawbench-hermes-agent-v0.5.tar.gz
```

### Download Task Data

Download the task data from [HuggingFace](https://huggingface.co/datasets/internlm/WildClawBench/tree/main/workspace):

```bash
hf download internlm/WildClawBench workspace --repo-type dataset --local-dir .
```

### Prepare Data

Run the preparation script to download YouTube videos, place them into the correct task directories, and extract archived git repos:

```bash
bash script/prepare.sh
```

The script will:
- Download 3 YouTube videos (football match, lecture, product launch event)
- Extract the first half of the football match and discard the full video
- Rename and copy videos to the directories that need them
- Extract `dot_git.tar.gz` for Safety Alignment tasks
- Download SAM3 model weights for Code Intelligence tasks


Prerequisites: `yt-dlp`, `ffmpeg`, `gdown`.

> **Note:** YouTube downloads may require authentication. If you encounter a "Sign in to confirm you're not a bot" error, try one of the following:
> - [Get cookies.txt locally](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc?pli=1).
> - Use `--cookies-from-browser` (e.g., `--cookies-from-browser chrome`)
> - Install [Deno](https://deno.land/) as a JS engine, which some users have reported resolves the issue

### Run

Set your API keys in the `.env` file:

```
OPENROUTER_API_KEY=your_api_key_here
BRAVE_API_KEY=your_brave_key_here  # required for search tasks
```

- **OpenRouter API Key** — Any model available on [OpenRouter](https://openrouter.ai/models) is supported. The default model is defined in the `.env` file as `DEFAULT_MODEL=openrouter/stepfun/step-3.5-flash:free` — replace it with any model you want to evaluate.
- **Brave Search API Key** — Required for Search & Retrieval tasks. Get one (with free monthly credits) at [brave.com/search/api](https://brave.com/search/api/).
- **Judge model** (optional) — `JUDGE_MODEL` controls the LLM used by judge-based grading metrics. Defaults to `openai/gpt-5.4`.

Then run one of the four harnesses:

```bash
bash script/run.sh openclaw     --category all --parallel 4 --model openrouter/openai/gpt-5.5
bash script/run.sh claudecode   --category all --parallel 4 --model openai/gpt-5.5
bash script/run.sh codex        --category all --parallel 4 --model openrouter/openai/gpt-5.5
bash script/run.sh hermesagent  --category all --parallel 4 --model openai/gpt-5.5
```

Single-task runs are also supported:

```bash
bash script/run.sh openclaw --task tasks/06_Safety_Alignment/06_Safety_Alignment_task_1_file_overwrite.md \
                            --model openrouter/openai/gpt-5.5
```

> Model-name conventions differ per harness:
> - **OpenClaw / Codex** expect `openrouter/<provider>/<model>` (since they hit OpenRouter directly).
> - **Claude Code / Hermes Agent** expect `<provider>/<model>` (the `openrouter/` prefix is added internally).

### Using a Custom Model Endpoint (Without OpenRouter)

This option currently applies to the **OpenClaw harness** only. If you prefer to use your own API endpoint instead of OpenRouter, you can provide a JSON file and WildClawBench will inject it into `~/.openclaw/openclaw.json` before each task starts.

⚠️ Important: Some task prompts and evaluation scripts currently have OpenRouter explicitly mentioned or hardcoded (e.g., https://openrouter.ai/api/v1). If you bypass OpenRouter, you will need to adjust these references in the respective files manually.

**1. Fill in `my_api.json` (or provide your own JSON file with the same format):**
```json
{
  "providers": {
    "my-openai-proxy": {
      "baseUrl": "http://host.docker.internal:8000/v1",
      "apiKey": "${MY_PROXY_API_KEY}",
      "api": "openai-completions",
      "models": [
        {
          "id": "my-model",
          "name": "My Model"
        }
      ]
    }
  }
}
```

This file is the value written into `openclaw.json["models"]`, so it should contain the `models` object itself, not the full `openclaw.json`. If you use `${MY_PROXY_API_KEY}`, WildClawBench will replace it on the host before the config is copied into the container, so `MY_PROXY_API_KEY` must be set in `.env`. WildClawBench always replaces the existing top-level `models` field with the JSON you provide.

**2. Set your model name and required API key in `.env`:**
```bash
MY_PROXY_API_KEY=your_api_key_here
```

**3. Run the benchmark with the models config file:**
```bash
python3 eval/run_batch.py --category 01_Productivity_Flow --models-config my_api.json --model my-openai-proxy/my-model
```

<details>
<summary>Common provider examples</summary>

OpenAI-compatible proxy:

```json
{
  "providers": {
    "proxy": {
      "baseUrl": "http://host.docker.internal:8000/v1",
      "models": [
        {
          "id": "gpt-4o",
          "name": "GPT-4o"
        }
      ]
    }
  }
}
```

Local vLLM or LM Studio:

```json
{
  "providers": {
    "local-openai": {
      "baseUrl": "http://host.docker.internal:1234/v1",
      "models": [
        {
          "id": "qwen2.5-coder-32b-instruct",
          "name": "Qwen2.5 Coder 32B Instruct"
        }
      ]
    }
  }
}
```

Provider with explicit API mode and env var key:

```json
{
  "providers": {
    "custom-gateway": {
      "baseUrl": "http://host.docker.internal:9000/v1",
      "apiKey": "${MY_PROXY_API_KEY}",
      "api": "openai-completions",
      "models": [
        {
          "id": "my-reasoning-model",
          "name": "My Reasoning Model"
        }
      ]
    }
  }
}
```

</details>

## Check the Results

After the run completes, a per-category summary and a global summary (`output/summary_all.json`) are generated automatically. Each metric is scored from `0.00` to `1.00`.

Per-task results are saved under `output/<harness>/<category>/<task_id>/<model_timestamp_runid>/`:

```
output/<harness>/<category>/<task_id>/<model_timestamp_runid>/
├── score.json          # per-metric scores
├── usage.json          # token counts, cost, elapsed time
├── agent.log           # agent execution log
├── chat.jsonl          # full conversation trace (OpenClaw)
├── claude_code_log/    # Claude Code session log (Claude Code)
├── codex_sessions/     # Codex session JSONLs (Codex)
├── gateway.log         # gateway log (OpenClaw)
└── task_output/        # files produced by the agent
```

The subdirectory name is `<short_model>_<timestamp>_<runid>`, where `short_model` is the last segment of the model path (e.g. `claude-sonnet-4.6` from `openrouter/anthropic/claude-sonnet-4.6`) and `runid` is a 6-char random hex string, so parallel or repeated runs never collide.

For independent verification and side-by-side comparison, we have provided the complete evaluation details and trajectories in our Google Drive folder:

- overall_results.json: [Overall Results](https://drive.google.com/file/d/1EI1_ABNLwEaiguzUU7f0RuEk5KFIMLUu/view?usp=drive_link)
- overall_dashboard.html: [Performance Dashboard](https://drive.google.com/file/d/1B7nStKfXeyATBM3lIv858M9FaH6QBPWU/view?usp=drive_link)
- gemini 3.1 Pro Details: [Gemini 3.1 Pro](https://drive.google.com/file/d/1STpQWocGn8XeGLHFX3AZfy2TB3Q0PsfO/view?usp=drive_link)
- GPT 5.4 Details: [GPT 5.4](https://drive.google.com/file/d/15zamWhsI5qJMon71N0AAs2Ysrfkns-1w/view?usp=drive_link)
- Kimi K2.5 Details: [Kimi K2.5](https://drive.google.com/file/d/1Ne7CkE6gtCNR7OQR4ZKcp7qXvNmive9Q/view?usp=drive_link)
- MiniMax M2.7 Details: [MiniMax M2.7](https://drive.google.com/file/d/15K65XZxkUqKWj3rp-d-gZN0DEL1iu2Kf/view?usp=drive_link)
- Claude Opus 4.6 Details: [Claude 4.6 Opus](https://drive.google.com/file/d/1qCPxy0-Z-LveiVAmPTVlrh3x2fe9qlU6/view?usp=drive_link)

More models's (fable5, glm5.2, gpt5.6, grok4.5, hy3, kimi_k3, muse_spark) details in [internlm/WildClawBench-Trajectories](https://huggingface.co/datasets/internlm/WildClawBench-Trajectories)

## Personal OpenClaw Evaluation

"Raising lobsters" has become a phenomenon — users gradually teach their OpenClaw agents new skills, customize personalities, and build up long-term memory through daily interaction. A natural question follows: **whose lobster is better?** Beyond bragging rights, there is real value in understanding which skill combinations, persona designs, and memory strategies actually improve agent performance on a given model. That's why we created the **Personal OpenClaw Leaderboard**. Submit your lobster's results and see how it stacks up!


```bash
python eval/run_batch.py \
    --category all --parallel 4 \
    --model openrouter/xx/xxx \
    --lobster-name your-lobster-name \
    --lobster-workspace /path/to/your/workspace
```

- `--lobster-name` — identifier, used in the output directory.
- `--lobster-workspace` — path to your OpenClaw workspace (containing `SOUL.md`, `USER.md`, `MEMORY.md`, `skills/`, etc.).
- `--lobster-env` — (optional) comma-separated env var names for skills that need API keys (e.g. `GEMINI_API_KEY,FIRECRAWL_API_KEY`). Add the actual values to `.env`.

After the run completes, send the following to **wildclawbench@proton.me**:

1. Your `output/summary_all_<lobster-name>_<model>.json`
2. (Optional) A brief description of how you trained your OpenClaw (e.g. key skills, custom SOUL.md, memory strategies).

We will update the leaderboard periodically.

---

## Citation

If you use WildClawBench in your research, please cite it as:

```bibtex
@article{ding2026wildclawbench,
  title={WildClawBench: A Benchmark for Real-World, Long-Horizon Agent Evaluation},
  author={Ding, Shuangrui and Dai, Xuanlang and Xing, Long and Ding, Shengyuan and Liu, Ziyu and JingYi, Yang and Yang, Penghui and Zhang, Zhixiong and Wei, Xilin and Fang, Xinyu and others},
  journal={arXiv preprint arXiv:2605.10912},
  year={2026}
}
```

For machine-readable citation metadata, see [`CITATION.cff`](CITATION.cff). GitHub will use this file to populate the repository's "Cite this repository" panel.

---

## Contributors

[Shuangrui Ding](https://mark12ding.github.io/)\* (Project Lead), [Xuanlang Dai](https://github.com/LennoxDai)\*, [Long Xing](https://github.com/Cooperx521)\*, [Shengyuan Ding](https://github.com/SYuan03), [Ziyu Liu](https://liuziyu77.github.io/), [Jingyi Yang](https://yjyddq.github.io/), [Penghui Yang](https://github.com/yph22), [Zhixiong Zhang](https://github.com/rookiexiong7), [Xilin Wei](https://github.com/wiselnn570), [Xinyu Fang](https://scholar.google.com/citations?user=QZk6nZ8AAAAJ&hl=zh-CN)

Advisors: [Yubo Ma](https://mayubo2333.github.io/), [Haodong Duan](https://kennymckormick.github.io/), [Jing Shao](https://amandajshao.github.io/), [Jiaqi Wang](https://myownskyw7.github.io/), [Dahua Lin](http://dahualin.org/), [Kai Chen](https://chenkai.site/), [Yuhang Zang](https://yuhangzang.github.io/)

---

## Acknowledgements

WildClawBench builds on top of the excellent open-source agent ecosystem. We gratefully acknowledge the following projects:

- **[OpenClaw](https://github.com/openclaw/openclaw)** 
- **[Claw-Eval](https://github.com/claw-eval/claw-eval)**
- **[PinchBench](https://github.com/pinchbench/skill)**
- **[Hermes-Agent](https://github.com/nousresearch/hermes-agent)**

---

## Cleanup

If a run is interrupted (e.g. `Ctrl+C`, terminal closed), some Docker containers may be left behind. To remove **all** WildClawBench containers when no tasks are running:

```bash
for img in \
    wildclawbench-ubuntu:v1.3 \
    wildclawbench-claudecode-ubuntu:v0.2 \
    wildclawbench-codex-ubuntu:v0.0 \
    wildclawbench-hermes-agent:v0.5; do
  docker ps -a --filter "ancestor=$img" -q | xargs -r docker rm -f
done
```

To preview which containers would be removed (dry run), drop the `docker rm -f` step and use `--format "{{.Names}}\t{{.Status}}"`.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---
## Star History

<a href="https://www.star-history.com/?repos=internlm%2FWildClawBench&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=internlm/WildClawBench&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=internlm/WildClawBench&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=internlm/WildClawBench&type=date&legend=top-left" />
 </picture>
</a>
