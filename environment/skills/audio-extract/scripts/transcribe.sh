#!/usr/bin/env bash
# Transcribe an audio/video file to text via the harness LiteLLM sidecar.
#
# Usage:
#   transcribe.sh <media>                 # audio OR video; auto-extracts WAV
#   transcribe.sh <media> --raw           # also print the raw sidecar JSON to stderr
#
# Output (stdout): the transcript text.
# Output (stderr): step markers ("== extract ==", "== transcribe ==") and,
#                  with --raw, the unparsed JSON response.
# Exit code: 0 on success; non-zero with a clear error on any failure.
#
# Design notes:
#   - Uses WCB_AUDIO_TRANSCRIBE_URL injected by the harness (openclaw runner).
#     URL points at the in-cluster LiteLLM sidecar's
#     /v1/audio/transcriptions endpoint, reachable over the --internal
#     Docker bridge. The sidecar holds the upstream API key; the agent
#     container has no internet egress and no key.
#   - If the input is already a WAV, we skip ffmpeg and post directly. Any
#     other extension (m4a, mp3, mp4, mov, wav with non-standard rate, etc.)
#     goes through ffmpeg -> 16kHz mono pcm_s16le, which is the format the
#     sidecar/whisper-1 backend expects. WAV at any rate also works for
#     whisper-1, but we re-encode for determinism and to keep the file under
#     OpenAI's 25 MB upload cap on long recordings.
#   - Response is parsed with python3 (always present in this image) to
#     avoid a jq dependency, which is NOT in wildclawbench-ubuntu:v1.3.

set -euo pipefail

if [[ "${1:-}" == "" || "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat >&2 <<'EOF'
usage: transcribe.sh <media> [--raw]

Transcribe an audio or video file to text via the harness LiteLLM sidecar.
The transcript is printed on stdout. With --raw, the unparsed JSON
response is also printed on stderr.
EOF
  exit 2
fi

in="$1"
raw_mode="0"
if [[ "${2:-}" == "--raw" ]]; then
  raw_mode="1"
fi

if [[ ! -f "$in" ]]; then
  echo "transcribe.sh: input file not found: $in" >&2
  exit 1
fi

url="${WCB_AUDIO_TRANSCRIBE_URL:-}"
if [[ -z "$url" ]]; then
  echo "transcribe.sh: WCB_AUDIO_TRANSCRIBE_URL is not set." >&2
  echo "  This env var is supposed to be injected by the harness at" >&2
  echo "  container start (openclaw runner -> start_container extra_env_dict)." >&2
  echo "  Without it, the agent has no working transcription path." >&2
  echo "  Treat as a harness configuration regression." >&2
  exit 3
fi

basename_in="$(basename "$in")"
stem="${basename_in%.*}"
scratch_dir="/tmp_workspace/_scratch"
mkdir -p "$scratch_dir"
wav="$scratch_dir/${stem}.wav"

echo "== extract: $in -> $wav ==" >&2
ffmpeg -y -loglevel error -i "$in" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$wav"

if [[ ! -s "$wav" ]]; then
  echo "transcribe.sh: ffmpeg produced no audio output for $in" >&2
  exit 4
fi

echo "== transcribe: POST $url (file=$wav, model=whisper-1) ==" >&2

# Use a temp file for the response so we can both inspect HTTP status and
# parse the body even on non-2xx. --fail-with-body would mix the two; safer
# to split with -w "%{http_code}" -o body_file.
resp_body="$(mktemp)"
trap 'rm -f "$resp_body"' EXIT

auth_header=()
if [[ -n "${WCB_AUDIO_TRANSCRIBE_AUTH:-}" ]]; then
  auth_header=(-H "Authorization: Bearer ${WCB_AUDIO_TRANSCRIBE_AUTH}")
fi

http_code="$(curl -sS \
  -w "%{http_code}" \
  -o "$resp_body" \
  "${auth_header[@]}" \
  -F "file=@${wav}" \
  -F "model=whisper-1" \
  -F "response_format=json" \
  "$url")" || {
    echo "transcribe.sh: curl transport error reaching $url" >&2
    echo "  Response body (if any):" >&2
    sed 's/^/    /' < "$resp_body" >&2 || true
    exit 5
  }

if [[ "$http_code" != "200" ]]; then
  echo "transcribe.sh: sidecar returned HTTP $http_code from $url" >&2
  echo "  Response body:" >&2
  sed 's/^/    /' < "$resp_body" >&2 || true
  exit 6
fi

if [[ "$raw_mode" == "1" ]]; then
  echo "== raw response ==" >&2
  cat "$resp_body" >&2
  echo >&2
fi

python3 - "$resp_body" <<'PY'
import json, sys
path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
text = data.get("text")
if text is None:
    sys.stderr.write(
        "transcribe.sh: sidecar response did not contain 'text' field.\n"
        f"  Keys present: {list(data.keys())}\n"
    )
    sys.exit(7)
sys.stdout.write(text)
if not text.endswith("\n"):
    sys.stdout.write("\n")
PY
