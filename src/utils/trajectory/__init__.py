"""Trajectory builder — produces schema-conformant multimodal trajectories
from OpenClaw JSONL session files.
"""

from src.utils.jsonl_reader import sanitize_jsonl_message
from .builder import build_trajectory_from_jsonl
from .local_media import replace_inline_media_with_files
from .multimodal_meta import (
    build_input_files_manifest,
    build_multimodal_metadata,
    build_output_artifacts,
    slugify_task_type,
)
from .s3_media import replace_inline_media_with_s3

__all__ = [
    "build_input_files_manifest",
    "build_multimodal_metadata",
    "build_output_artifacts",
    "build_trajectory_from_jsonl",
    "replace_inline_media_with_files",
    "replace_inline_media_with_s3",
    "sanitize_jsonl_message",
    "slugify_task_type",
]
