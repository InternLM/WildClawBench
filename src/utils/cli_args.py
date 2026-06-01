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
        choices=["openclaw", "claudecode", "codex", "hermesagent"],
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
        default="xhigh",
        help="Thinking/reasoning level set as agents.defaults.thinkingDefault "
             "(default: xhigh, matching the kensei harness). Use 'off' to disable.",
    )
    parser.add_argument(
        "--openclaw-image-model",
        default=None,
        help="Optional OpenClaw image tool model. If unset, falls back to the chat --model.",
    )

    # ---- LiteLLM / Bedrock routing (openclaw backend) ----
    routing = parser.add_mutually_exclusive_group()
    routing.add_argument(
        "--litellm",
        dest="litellm",
        action="store_true",
        default=None,
        help="Force routing via the shared LiteLLM sidecar (Bedrock/OpenAI). "
             "Default: auto-enable when Bedrock/OpenAI env is configured.",
    )
    routing.add_argument(
        "--no-litellm",
        dest="litellm",
        action="store_false",
        help="Force OpenRouter routing even if Bedrock/OpenAI env is set.",
    )
    parser.add_argument(
        "--bedrock-arn",
        default=None,
        help="Override the Bedrock inference-profile ARN (else BEDROCK_MODEL_ARN env).",
    )
    parser.add_argument(
        "--aws-region",
        default=None,
        help="Override the AWS region for Bedrock (else AWS_REGION env, default ap-south-1).",
    )
    parser.add_argument(
        "--mock-stack",
        dest="mock_stack",
        action="store_true",
        default=False,
        help="Run all required mock APIs in one shared container on the run network.",
    )
    testgen = parser.add_mutually_exclusive_group()
    testgen.add_argument(
        "--generate-tests",
        dest="generate_tests",
        action="store_true",
        default=None,
        help="Run kensei2 test generation via Bedrock for each task before the agent runs "
             "(populates task.test_code and task.test_weights so harbor can bundle them). "
             "Default: auto-enable when Bedrock env is configured.",
    )
    testgen.add_argument(
        "--no-generate-tests",
        dest="generate_tests",
        action="store_false",
        help="Skip test generation even when Bedrock env is configured.",
    )
    parser.add_argument(
        "--testgen-max-attempts",
        type=int,
        default=3,
        metavar="N",
        help="Max LLM retry attempts for test generation lint loop (default: 3).",
    )
    testexec = parser.add_mutually_exclusive_group()
    testexec.add_argument(
        "--execute-tests",
        dest="execute_tests",
        action="store_true",
        default=None,
        help="After the agent finishes, run the generated test_outputs.py against "
             "the workspace + live mock stack to compute a real pytest reward "
             "(reward.txt + ctrf.json). Default: auto-enable when --generate-tests "
             "and --mock-stack are both on.",
    )
    testexec.add_argument(
        "--no-execute-tests",
        dest="execute_tests",
        action="store_false",
        help="Skip test execution (rubric judge only).",
    )
    parser.add_argument(
        "--testexec-timeout",
        type=int,
        default=600,
        metavar="SEC",
        help="Outer cap on the test-runner subprocess (default: 600s). Per-test budget is set via WCB_PER_TEST_TIMEOUT inside the runner (default: 30s).",
    )
    parser.add_argument(
        "--rebuild-mocks",
        dest="rebuild_mocks",
        action="store_true",
        default=False,
        help="Force-rebuild the mock-API image even if the cached tag exists "
             "(use after editing environment/<api>/ server code or baseline CSVs).",
    )
    return parser


def parse_run_batch_args(default_model: str, default_parallel: int) -> argparse.Namespace:
    return build_run_batch_parser(default_model, default_parallel).parse_args()
