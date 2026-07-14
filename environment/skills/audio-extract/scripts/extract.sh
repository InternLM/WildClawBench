#!/usr/bin/env bash
# Extract a mono 16kHz WAV audio track from a media file, and/or probe metadata.
#   extract.sh <media> [out.wav]     -> probe + extract audio
#   extract.sh --probe <media>       -> probe only
set -euo pipefail

if [[ "${1:-}" == "--probe" ]]; then
  in="${2:?usage: extract.sh --probe <media>}"
  ffprobe -v error -show_entries \
    format=duration,format_name,bit_rate -show_streams "$in"
  exit 0
fi

in="${1:?usage: extract.sh <media> [out.wav]}"
out="${2:-/tmp/audio.wav}"
mkdir -p "$(dirname "$out")"

echo "== probe ==" >&2
ffprobe -v error -show_entries format=duration,format_name -of default=nw=1 "$in" >&2 || true

echo "== extract audio -> $out ==" >&2
ffmpeg -y -loglevel error -i "$in" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$out"
echo "$out"
