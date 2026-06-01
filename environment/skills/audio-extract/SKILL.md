---
name: audio-extract
description: Extract the audio track from a video/media file and probe media metadata using ffmpeg/ffprobe.
metadata: {"clawdbot":{"emoji":"🎧","requires":{"bins":["ffmpeg","ffprobe"]},"install":[{"id":"brew","kind":"brew","formula":"ffmpeg","bins":["ffmpeg"],"label":"Install ffmpeg (brew)"}]}}
---

# Audio Extract (ffmpeg)

Pull a clean mono 16kHz WAV audio track out of any video/media file (ready for
transcription by a multimodal model), and print media metadata.

## Quick start

```bash
{baseDir}/scripts/extract.sh /path/to/recording.mp4 /tmp_workspace/results/audio.wav
```

Probe only (duration, streams, codecs):

```bash
{baseDir}/scripts/extract.sh --probe /path/to/recording.mp4
```

The 16kHz mono WAV is the standard input format for speech-to-text. Pass the
resulting audio to the multimodal model for transcription. Requires `ffmpeg`.
