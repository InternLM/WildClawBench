---
name: audio-extract
description: Extract a 16kHz mono WAV audio track from any media file, probe metadata, and transcribe speech to text via the harness-provided LiteLLM sidecar (no internet required from inside the agent container).
metadata: {"clawdbot":{"emoji":"🎧","requires":{"bins":["ffmpeg","ffprobe","curl"],"env":["WCB_AUDIO_TRANSCRIBE_URL","WCB_AUDIO_TRANSCRIBE_AUTH"]},"install":[{"id":"brew","kind":"brew","formula":"ffmpeg","bins":["ffmpeg"],"label":"Install ffmpeg (brew)"}]}}
---

# Audio Extract & Transcribe

This skill turns any audio/video file into (a) a clean 16kHz mono WAV and
(b) a plain-text transcript. Both steps run entirely inside the sandbox: the
WAV is produced locally by `ffmpeg`, and the transcript is fetched from the
harness-provided LiteLLM sidecar over the internal Docker bridge. The agent
container has **no direct internet access** — do NOT try `pip install
openai-whisper`, `pip install pypdf`, or `curl https://api.openai.com/...`;
those all fail with `Temporary failure in name resolution`. The sidecar
route below is the supported transcription path.

## Quick start — transcribe (most common case)

```bash
{baseDir}/scripts/transcribe.sh /path/to/recording.m4a
```

Output (stdout): the transcript text, one block.
The intermediate WAV is left at `/tmp_workspace/_scratch/<basename>.wav` so
you can re-use it (e.g. send a second pass with different prompt context).

## Probe only (metadata, no extraction, no transcription)

```bash
{baseDir}/scripts/extract.sh --probe /path/to/recording.mp4
```

Prints duration, format, codecs, stream count.

## Extract only (no transcription) — useful when you want to control the WAV path

```bash
{baseDir}/scripts/extract.sh /path/to/recording.mp4 /tmp_workspace/results/audio.wav
```

The 16kHz mono WAV is the standard input format for speech-to-text. If you
have already produced a WAV yourself, you can transcribe it directly:

```bash
{baseDir}/scripts/transcribe.sh /tmp_workspace/results/audio.wav
```

## How transcription works (so you can debug if it fails)

The transcribe step `POST`s a multipart form to
`$WCB_AUDIO_TRANSCRIBE_URL` (set by the harness, points at the LiteLLM
sidecar's `/v1/audio/transcriptions` endpoint). The sidecar holds the
upstream API key; you don't need one in the agent container. Model is
`whisper-1`. Response is JSON: `{"text": "<transcript>"}`. The script
extracts `.text` and prints it on stdout.

```bash
curl -s --fail \
  -H "Authorization: Bearer $WCB_AUDIO_TRANSCRIBE_AUTH" \
  -F "file=@/path/to/audio.wav" \
  -F "model=whisper-1" \
  -F "response_format=json" \
  "$WCB_AUDIO_TRANSCRIBE_URL"
```

If `WCB_AUDIO_TRANSCRIBE_URL` is unset, `transcribe.sh` will print a clear
error and exit non-zero. That means the harness did not wire the sidecar
URL (a configuration regression — flag it in your final answer rather than
silently dropping the audio content).

If the POST itself fails (network error, sidecar down, HTTP 4xx/5xx),
`transcribe.sh` prints the curl error and the response body, then exits
non-zero. Common causes:

- `Could not resolve host` — sidecar container name is unreachable from
  this agent container. The bridge network was not created or the sidecar
  is not joined. Treat as a harness bug.
- `HTTP 401/403` from upstream — the sidecar has no valid upstream API
  key. Treat as a harness bug; do not attempt to call OpenAI directly
  from the agent container (no internet egress).
- `HTTP 400 Invalid model name` — the sidecar config did not register
  `whisper-1`. Treat as a harness bug.

## Fallback: local Whisper (only if the sidecar route is unavailable)

There are two `whisper` skills shipped inside the openclaw runtime
(`openai-whisper`, `openai-whisper-api`) but **neither works in this
sandbox**:

- `openai-whisper` wants the `whisper` CLI binary, which is not installed
  in `wildclawbench-ubuntu:v1.3` and cannot be pip-installed (no
  internet).
- `openai-whisper-api` wants `OPENAI_API_KEY` plus a direct HTTPS call to
  `api.openai.com`, neither of which is available in the agent
  container.

If you encounter a run where the primary sidecar route fails AND the
harness has staged a local Whisper wheelhouse + model weights (look for
`/opt/wb_whisper_models/` and a `whisper` import that succeeds), then
local transcription is possible:

```python
import whisper
model = whisper.load_model("small", download_root="/opt/wb_whisper_models")
print(model.transcribe("/path/to/audio.wav")["text"])
```

This is a contingency path. The supported route is the sidecar.

## Requires

- `ffmpeg`, `ffprobe` — installed in the image. Used by both
  `extract.sh` and `transcribe.sh`.
- `curl` — installed in the image. Used by `transcribe.sh`.
- `WCB_AUDIO_TRANSCRIBE_URL` — exported into the agent container by the
  harness at startup; points at the in-cluster LiteLLM sidecar's
  `/v1/audio/transcriptions` endpoint.
- `WCB_AUDIO_TRANSCRIBE_AUTH` — exported into the agent container by the
  harness at startup; bearer token for the sidecar's master_key auth.
