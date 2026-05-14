from __future__ import annotations

import argparse


def build_run_batch_parser(default_model: str, default_parallel: int) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ClawBench evaluation entry point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--task", "-t", help="Path to a single task.md file")
    mode.add_argument(
        "--category",
        "-c",
        help="Category name, e.g. 01_Productivity_Flow, 02_Code_Intelligence, 03_Social_Interaction, 04_Search_Retrieval, 05_Creative_Synthesis, 06_Safety_Alignment",
    )

    parser.add_argument(
        "--agent-backend",
        default="openclaw",
        choices=["openclaw", "claudecode", "codex", "hermesagent", "commander"],
        help="Agent backend implementation (default: openclaw)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default=default_model,
        help=f"Model name (default: {default_model})",
    )
    parser.add_argument(
        "--parallel",
        "-p",
        type=int,
        default=default_parallel,
        metavar="N",
        help="Number of parallel containers (default: 1, i.e. sequential)",
    )
    parser.add_argument(
        "--lobster-name",
        default=None,
        help="Lobster name (used in output directory for comparison)",
    )
    parser.add_argument(
        "--lobster-workspace",
        default=None,
        help="Path to a personal OpenClaw workspace (contains SOUL.md, USER.md, etc.)",
    )
    parser.add_argument(
        "--lobster-env",
        default=None,
        help="Comma-separated env var names for skills that need API keys (e.g. GEMINI_API_KEY,FIRECRAWL_API_KEY)",
    )
    parser.add_argument(
        "--models-config",
        default=None,
        help="Path to a JSON file that will replace the top-level models field in ~/.openclaw/openclaw.json before each task",
    )
    parser.add_argument(
        "--thinking",
        default=None,
        help="Thinking/reasoning level for the model (default: high)",
    )
    parser.add_argument(
        "--openclaw-image-model",
        default=None,
        help="Optional OpenClaw image tool model. If unset, falls back to the chat --model.",
    )
    return parser


def parse_run_batch_args(default_model: str, default_parallel: int) -> argparse.Namespace:
    return build_run_batch_parser(default_model, default_parallel).parse_args()
