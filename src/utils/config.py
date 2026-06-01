from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from dotenv import dotenv_values
except ImportError:
    def dotenv_values(path):  # type: ignore[misc]
        out: dict = {}
        if not os.path.isfile(path):
            return out
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
        return out


# src/utils/config.py -> parents[2] == repo root (Wildclow_forked_image)
ROOT_DIR = Path(__file__).resolve().parents[2]
ENVIRONMENT_DIR = ROOT_DIR / "environment"


@dataclass
class Config:
    # ---- AWS Bedrock (Claude via bearer token) ----
    bedrock_inference_arn: str = ""
    bedrock_sonnet_arn: str = ""
    bedrock_region: str = "ap-south-1"
    aws_bearer_token: str = ""

    # ---- S3 (trajectory media upload) ----
    s3_bucket: str = ""
    s3_prefix: str = "WildClaw"
    s3_region: str = "us-east-1"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""

    # ---- OpenAI (direct / via-LiteLLM) ----
    openai_api_key: str = ""

    # ---- OpenRouter (fallback LLM routing) ----
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # ---- Brave Search (passed to container; placeholder prevents gateway crash) ----
    brave_api_key: str = "placeholder"

    # ---- Container image ----
    docker_image: str = "wildclawbench-ubuntu:v1.3"

    # ---- LiteLLM proxy (shared sidecar container) ----
    litellm_master_key: str = "sk-talos-litellm"
    litellm_port: int = 4000

    # ---- Sandbox runtime ----
    tmp_workspace: str = "/tmp_workspace"
    gateway_port: int = 18789

    # ---- Harbor quality gate ----
    min_harbor_score: float | None = None

    # ---- File paths ----
    environment_dir: Path = field(default_factory=lambda: ENVIRONMENT_DIR)
    state_db: Path = field(default_factory=lambda: ROOT_DIR / "state.db")
    work_dir: Path = field(default_factory=lambda: ROOT_DIR / "work")
    output_dir: Path = field(default_factory=lambda: ROOT_DIR / "output")

    # ---- WildClawBench skills ----
    wildclaw_skills_dir: Path | None = None
    default_skills: list = field(default_factory=list)

    # ---- Behaviour ----
    upload_media_to_s3: bool = False

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Config":
        env: dict = {}
        if env_file is None:
            for candidate in (ROOT_DIR / ".env", Path.cwd() / ".env"):
                if candidate.is_file():
                    env_file = candidate
                    break
        if env_file and Path(env_file).is_file():
            env.update(dotenv_values(env_file))
        env.update(os.environ)

        def s(*keys: str, default: str = "") -> str:
            for k in keys:
                v = env.get(k)
                if v not in (None, ""):
                    return str(v).strip()
            return default

        def b(key: str, default: bool) -> bool:
            v = env.get(key)
            if v is None:
                return default
            return str(v).strip().lower() in ("1", "true", "yes", "on")

        def i(key: str, default: int) -> int:
            v = env.get(key)
            if v is None:
                return default
            try:
                return int(v)
            except ValueError:
                return default

        def f(key: str, default: float | None = None) -> float | None:
            v = env.get(key)
            if v in (None, ""):
                return default
            try:
                return float(v)
            except ValueError:
                return default

        _wcsd = s("WILDCLAW_SKILLS_DIR")
        # Media-processing skills injected into every task by default (e.g.
        # video-frames = ffmpeg frame/clip extraction for multimodal inputs).
        _ds = s("WILDCLAW_DEFAULT_SKILLS", "KENSEI3_DEFAULT_SKILLS",
                default="video-frames,pdf-extract,audio-extract")
        return cls(
            bedrock_inference_arn=s("KENSEI_BEDROCK_MODEL_ARN", "KENSEI2_BEDROCK_MODEL_ARN", "BEDROCK_MODEL_ARN"),
            bedrock_sonnet_arn=s("KENSEI_BEDROCK_SONNET_ARN", "BEDROCK_SONNET_ARN"),
            bedrock_region=s("KENSEI_AWS_REGION", "AWS_REGION", default="ap-south-1"),
            aws_bearer_token=s("KENSEI_AWS_BEARER_TOKEN", "AWS_BEARER_TOKEN_BEDROCK"),
            s3_bucket=s("S3_BUCKET"),
            s3_prefix=s("S3_PREFIX", default="WildClaw"),
            s3_region=s("S3_REGION", default="us-east-1"),
            s3_access_key_id=s("KENSEI_S3_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID"),
            s3_secret_access_key=s("KENSEI_S3_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY"),
            openai_api_key=s("KENSEI_OPENAI_API_KEY", "OPENAI_API_KEY"),
            openrouter_api_key=s("OPENROUTER_API_KEY"),
            openrouter_base_url=s("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1"),
            brave_api_key=s("BRAVE_API_KEY", default="placeholder"),
            docker_image=s("DOCKER_IMAGE", default="wildclawbench-ubuntu:v1.3"),
            tmp_workspace=s("TMP_WORKSPACE", default="/tmp_workspace"),
            gateway_port=i("GATEWAY_PORT", 18789),
            upload_media_to_s3=b("UPLOAD_MEDIA_TO_S3", False),
            # Skills live in the environment folder (the mock-API connectors).
            # Default the harness skill catalog to <root>/environment/skills.
            wildclaw_skills_dir=Path(_wcsd) if _wcsd else (ENVIRONMENT_DIR / "skills"),
            default_skills=[x.strip() for x in _ds.split(",") if x.strip()],
            litellm_master_key=s("KENSEI_LITELLM_MASTER_KEY", "KENSEI3_LITELLM_MASTER_KEY", "LITELLM_MASTER_KEY", default="sk-talos-litellm"),
            litellm_port=i("KENSEI3_LITELLM_PORT", i("LITELLM_PORT", 4000)),
            min_harbor_score=f("MIN_HARBOR_SCORE"),
        )

    def litellm_enabled(self) -> bool:
        """LiteLLM/Bedrock routing is active when Bedrock (arn+bearer token)
        OR a direct OpenAI key is configured. Otherwise OpenRouter is used."""
        if self.bedrock_inference_arn and self.aws_bearer_token:
            return True
        if self.openai_api_key:
            return True
        return False

    def ensure_dirs(self) -> None:
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
