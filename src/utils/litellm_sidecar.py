from __future__ import annotations

import logging
import subprocess
import time

logger = logging.getLogger(__name__)

LITELLM_IMAGE = "ghcr.io/berriai/litellm:main-stable"
LITELLM_INTERNAL_PORT = 4000


def build_litellm_config_yaml(
    bedrock_arn: str = "",
    aws_region: str = "ap-south-1",
    openai_api_key: str = "",
    bedrock_sonnet_arn: str = "",
    enable_usage_callback: bool = False,
) -> str:
    model_blocks: list[str] = []
    if bedrock_arn:
        model_blocks.append(
            "  - model_name: claude-opus-4.7\n"
            "    litellm_params:\n"
            f"      model: bedrock/converse/{bedrock_arn}\n"
            f"      aws_region_name: {aws_region or 'ap-south-1'}\n"
            "      thinking: {\"type\": \"adaptive\", \"display\": \"summarized\"}\n"
            "      stream_options:\n"
            "        include_usage: true\n"
            "      input_cost_per_token: 0.000005\n"
            "      output_cost_per_token: 0.000025"
        )
    if bedrock_sonnet_arn:
        model_blocks.append(
            "  - model_name: claude-sonnet-4-6\n"
            "    litellm_params:\n"
            f"      model: bedrock/converse/{bedrock_sonnet_arn}\n"
            f"      aws_region_name: {aws_region or 'ap-south-1'}\n"
            "      thinking: {\"type\": \"adaptive\", \"display\": \"summarized\"}\n"
            "      stream_options:\n"
            "        include_usage: true\n"
            "      input_cost_per_token: 0.000003\n"
            "      output_cost_per_token: 0.000015"
        )
    if openai_api_key:
        # OpenAI Responses API needs BOTH effort AND summary to emit reasoning
        # text. String form `reasoning_effort: high` returns hidden reasoning;
        # dict form below requests summary="detailed". Paired with the global
        # `reasoning_auto_summary: true` setting for the /v1/messages adapter.
        model_blocks.append(
            "  - model_name: gpt-5.5\n"
            "    litellm_params:\n"
            "      model: openai/gpt-5.5\n"
            "      api_key: os.environ/OPENAI_API_KEY\n"
            "      reasoning_effort: {\"effort\": \"high\", \"summary\": \"detailed\"}\n"
            "      stream_options:\n"
            "        include_usage: true\n"
            "      input_cost_per_token: 0.000005\n"
            "      output_cost_per_token: 0.00003"
        )
        # Without this, /v1/audio/transcriptions returns HTTP 400 "Invalid
        # model name passed in model=whisper-1" (see failure report §6a) and
        # the agent burns its budget on broken pip-install whisper fallbacks.
        model_blocks.append(
            "  - model_name: whisper-1\n"
            "    litellm_params:\n"
            "      model: openai/whisper-1\n"
            "      api_key: os.environ/OPENAI_API_KEY"
        )
    # OpenClaw's image tool falls back to a built-in default model id
    # ("anthropic/gpt-4o") when its own imageModel override isn't applied inside
    # the container. The gateway doesn't expose that id, so multimodal calls die
    # with "Unknown model: anthropic/gpt-4o" (see failure reports). Alias it to a
    # real vision-capable model that IS registered so image tasks resolve instead
    # of erroring. Prefer GPT-5.5 (OpenAI), else the Opus inference profile.
    if openai_api_key:
        image_alias = (
            "      model: openai/gpt-5.5\n"
            "      api_key: os.environ/OPENAI_API_KEY"
        )
    elif bedrock_arn:
        image_alias = (
            f"      model: bedrock/converse/{bedrock_arn}\n"
            f"      aws_region_name: {aws_region or 'ap-south-1'}"
        )
    else:
        image_alias = ""
    if image_alias:
        model_blocks.append(
            "  - model_name: anthropic/gpt-4o\n"
            "    litellm_params:\n"
            + image_alias
        )
    if not model_blocks:
        return ""
    # Real per-call usage from the proxy itself (not the agent's chat.jsonl
    # which openclaw writes with all-zero usage). Loaded by the LiteLLM
    # callback file mounted at /app/litellm_usage_callback.py.
    callback_line = (
        '  callbacks: ["litellm_usage_callback.proxy_handler_instance"]\n'
        if enable_usage_callback else ""
    )
    return (
        "model_list:\n"
        + "\n".join(model_blocks)
        + "\n"
        "litellm_settings:\n"
        "  drop_params: true\n"
        "  modify_params: true\n"
        "  telemetry: false\n"
        "  num_retries: 1\n"
"  request_timeout: 900\n"
"  stream_timeout: 300\n"
        "  reasoning_auto_summary: true\n"
        + callback_line
        + "general_settings:\n"
        "  master_key: os.environ/LITELLM_MASTER_KEY\n"
        "  store_model_in_db: false\n"
    )


def create_network(name: str) -> None:
    r = subprocess.run(
        ["docker", "network", "inspect", name],
        capture_output=True,
    )
    if r.returncode == 0:
        return
    r = subprocess.run(
        ["docker", "network", "create", name],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Failed to create network {name}: {r.stderr}")
    logger.info("Network %s created", name)


def remove_network(name: str) -> None:
    subprocess.run(["docker", "network", "rm", name], capture_output=True)


def start_litellm(
    container_name: str,
    network: str,
    host_config_path: str,
    master_key: str,
    aws_bearer_token: str = "",
    aws_region: str = "ap-south-1",
    openai_api_key: str = "",
    port: int = LITELLM_INTERNAL_PORT,
    usage_callback_host_path: str = "",
    usage_log_host_dir: str = "",
) -> None:
    env_args: list[str] = ["-e", f"LITELLM_MASTER_KEY={master_key}"]
    if aws_bearer_token:
        env_args += [
            "-e", f"AWS_BEARER_TOKEN_BEDROCK={aws_bearer_token}",
            "-e", f"AWS_REGION={aws_region}",
        ]
    if openai_api_key:
        env_args += ["-e", f"OPENAI_API_KEY={openai_api_key}"]

    # Mount the callback module + writable log dir so UsageWriter can write
    # real provider-side usage rows from inside the sidecar. The env var name
    # is also read by litellm_usage_callback.py:_write_row.
    callback_args: list[str] = []
    if usage_callback_host_path and usage_log_host_dir:
        callback_args = [
            "-v", f"{usage_callback_host_path}:/app/litellm_usage_callback.py:ro",
            "-v", f"{usage_log_host_dir}:/var/litellm_usage",
            "-e", "LITELLM_USAGE_LOG_PATH=/var/litellm_usage/usage.jsonl",
        ]

    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "--network", network,
        *env_args,
        *callback_args,
        "-v", f"{host_config_path}:/app/config.yaml:ro",
        LITELLM_IMAGE,
        "--config", "/app/config.yaml",
        "--port", str(port),
    ]
    logger.info("[%s] Starting LiteLLM sidecar on network %s", container_name, network)
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"LiteLLM container start failed:\n{r.stderr}")


def wait_for_litellm_healthy(container_name: str, port: int = LITELLM_INTERNAL_PORT,
                             timeout: float = 60.0) -> bool:
    probe = (
        "import sys, urllib.request; "
        "urllib.request.urlopen("
        f"'http://localhost:{port}/health/liveliness', timeout=2"
        ")"
    )
    deadline = time.time() + timeout
    interval = 2.0
    while time.time() < deadline:
        r = subprocess.run(
            ["docker", "exec", container_name, "python3", "-c", probe],
            capture_output=True,
        )
        if r.returncode == 0:
            logger.info("[%s] LiteLLM healthy", container_name)
            return True
        time.sleep(interval)
    logger.warning(
        "[%s] LiteLLM did not become healthy within %.0fs", container_name, timeout
    )
    return False


def stop_litellm(container_name: str) -> None:
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
