from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values


ROOT_DIR = Path(__file__).resolve().parent.parent

ALL_CATEGORIES = {
    "01_Productivity_Flow",
    "02_Code_Intelligence",
    "03_Social_Interaction",
    "04_Search_Retrieval",
    "05_Creative_Synthesis",
    "06_Safety_Alignment",
}

HARNESS_IMAGES = {
    "openclaw": ("DOCKER_IMAGE", "wildclawbench-ubuntu:v1.3"),
    "claudecode": ("DOCKER_IMAGE_CLAUDECODE", "wildclawbench-claudecode-ubuntu:v0.2"),
    "codex": ("DOCKER_IMAGE_CODEX", "wildclawbench-codex-ubuntu:v0.0"),
    "hermesagent": ("HERMES_DOCKER_IMAGE", "wildclawbench-hermes-agent:v0.5"),
}

PREPARE_COMMANDS = ("hf", "yt-dlp", "ffmpeg", "modelscope")


class Reporter:
    def __init__(self) -> None:
        self.failures = 0
        self.warnings = 0

    def ok(self, message: str) -> None:
        print(f"[OK]   {message}")

    def warn(self, message: str) -> None:
        self.warnings += 1
        print(f"[WARN] {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print(f"[FAIL] {message}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check local WildClawBench setup before launching a benchmark run."
    )
    parser.add_argument(
        "--agent-backend",
        default="openclaw",
        choices=sorted(HARNESS_IMAGES),
        help="Harness to check (default: openclaw).",
    )
    parser.add_argument(
        "--category",
        default="all",
        help="Category to check, or all (default: all).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model that will be passed to run_batch.py. Used for placeholder checks.",
    )
    parser.add_argument(
        "--models-config",
        default=None,
        help="Optional custom OpenClaw models config JSON path.",
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Skip Docker daemon and image checks.",
    )
    parser.add_argument(
        "--skip-images",
        action="store_true",
        help="Skip checking whether the selected harness image is loaded.",
    )
    parser.add_argument(
        "--skip-data",
        action="store_true",
        help="Skip checking workspace task data.",
    )
    return parser


def merged_env() -> dict[str, str]:
    env_file = ROOT_DIR / ".env"
    parsed = {
        key: value or ""
        for key, value in dotenv_values(env_file).items()
        if key
    }
    merged = {**parsed, **os.environ}
    return {key: str(value) for key, value in merged.items()}


def env_value(env: dict[str, str], key: str, default: str = "") -> str:
    return env.get(key, default).strip()


def run_quiet(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def check_repo_layout(report: Reporter) -> None:
    required_paths = [
        ROOT_DIR / "README.md",
        ROOT_DIR / ".env.example",
        ROOT_DIR / "eval" / "run_batch.py",
        ROOT_DIR / "script" / "run.sh",
        ROOT_DIR / "script" / "prepare.sh",
        ROOT_DIR / "tasks",
    ]
    for path in required_paths:
        if path.exists():
            report.ok(f"found {path.relative_to(ROOT_DIR)}")
        else:
            report.fail(f"missing {path.relative_to(ROOT_DIR)}")


def check_env_file(report: Reporter, env: dict[str, str], args: argparse.Namespace) -> None:
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        report.ok(".env exists")
    else:
        report.warn("no .env file found; copy .env.example to .env or export variables in your shell")

    if env_value(env, "OPENROUTER_API_KEY"):
        report.ok("OPENROUTER_API_KEY is set")
    else:
        report.fail("OPENROUTER_API_KEY is empty; most harnesses and judge checks need it")

    base_url = env_value(env, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    if base_url.startswith(("http://", "https://")):
        report.ok(f"OPENROUTER_BASE_URL is set to {base_url}")
    else:
        report.fail("OPENROUTER_BASE_URL must start with http:// or https://")

    if args.category in ("all", "04_Search_Retrieval"):
        if env_value(env, "BRAVE_API_KEY"):
            report.ok("BRAVE_API_KEY is set for Search & Retrieval tasks")
        else:
            report.fail("BRAVE_API_KEY is empty; Search & Retrieval tasks require Brave Search")

    model = args.model or env_value(env, "DEFAULT_MODEL")
    if not model:
        report.fail("no model provided and DEFAULT_MODEL is empty")
    elif model in {"openrouter/xxx", "xxx"}:
        report.warn("DEFAULT_MODEL still looks like a placeholder; pass --model or update .env")
    else:
        report.ok(f"model value is available: {model}")

    if args.models_config:
        models_config = (ROOT_DIR / args.models_config).resolve()
        if models_config.exists():
            report.ok(f"models config exists: {models_config}")
            raw = models_config.read_text(encoding="utf-8")
            if "${MY_PROXY_API_KEY}" in raw and not env_value(env, "MY_PROXY_API_KEY"):
                report.fail("models config uses ${MY_PROXY_API_KEY}, but MY_PROXY_API_KEY is empty")
        else:
            report.fail(f"models config not found: {models_config}")


def resolve_image(env: dict[str, str], backend: str) -> str:
    key, default = HARNESS_IMAGES[backend]
    if backend == "claudecode":
        return env_value(env, "DOCKER_IMAGE_CLAUDECODE") or env_value(
            env, "CLAUDECODE_DOCKER_IMAGE", default
        )
    return env_value(env, key, default)


def check_docker(report: Reporter, env: dict[str, str], args: argparse.Namespace) -> None:
    if args.skip_docker:
        report.warn("Docker checks skipped")
        return

    if not shutil.which("docker"):
        report.fail("docker command not found")
        return
    report.ok("docker command found")

    info = run_quiet(["docker", "info"])
    if info.returncode != 0:
        report.fail("Docker daemon is not reachable; start Docker Desktop or the Docker service")
        return
    report.ok("Docker daemon is reachable")

    if args.skip_images:
        report.warn("Docker image check skipped")
        return

    image = resolve_image(env, args.agent_backend)
    inspected = run_quiet(["docker", "image", "inspect", image])
    if inspected.returncode == 0:
        report.ok(f"Docker image loaded for {args.agent_backend}: {image}")
    else:
        report.fail(
            f"Docker image not loaded for {args.agent_backend}: {image}. "
            "Download the matching tarball from HuggingFace and run docker load."
        )


def check_workspace_data(report: Reporter, args: argparse.Namespace) -> None:
    tasks_dir = ROOT_DIR / "tasks"
    category = args.category
    if category != "all" and category not in ALL_CATEGORIES:
        report.fail(f"unknown category: {category}")
        return

    if category == "all":
        missing_task_dirs = [name for name in sorted(ALL_CATEGORIES) if not (tasks_dir / name).is_dir()]
        if missing_task_dirs:
            report.fail(f"missing task category directories: {', '.join(missing_task_dirs)}")
        else:
            report.ok("all task category directories are present")
    else:
        if (tasks_dir / category).is_dir():
            report.ok(f"task category directory exists: tasks/{category}")
        else:
            report.fail(f"missing task category directory: tasks/{category}")

    if args.skip_data:
        report.warn("workspace data checks skipped")
        return

    workspace_dir = ROOT_DIR / "workspace"
    if workspace_dir.is_dir():
        report.ok("workspace data directory exists")
    else:
        report.fail("workspace data directory is missing; run: hf download internlm/WildClawBench workspace --repo-type dataset --local-dir .")

    images_dir = ROOT_DIR / "Images"
    if images_dir.is_dir():
        report.ok("Images directory exists")
    else:
        report.warn("Images directory is missing; this is expected before downloading Docker image tarballs")


def check_prepare_commands(report: Reporter) -> None:
    for command in PREPARE_COMMANDS:
        if shutil.which(command):
            report.ok(f"{command} command found")
        else:
            report.warn(f"{command} command not found; install it before running script/prepare.sh")


def main() -> int:
    args = build_parser().parse_args()
    env = merged_env()
    report = Reporter()

    print("WildClawBench setup check")
    print(f"repo: {ROOT_DIR}")
    print(f"harness: {args.agent_backend}")
    print(f"category: {args.category}")
    print("")

    check_repo_layout(report)
    check_env_file(report, env, args)
    check_docker(report, env, args)
    check_workspace_data(report, args)
    check_prepare_commands(report)

    print("")
    if report.failures:
        print(f"Setup check failed: {report.failures} failure(s), {report.warnings} warning(s).")
        return 1
    print(f"Setup check passed with {report.warnings} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
