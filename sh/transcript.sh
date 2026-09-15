#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

WHISPER_DIR="$ROOT_DIR/whisper.cpp"
WHISPER_BIN="$WHISPER_DIR/build/bin/whisper-cli"
MODEL="$WHISPER_DIR/models/ggml-base.en.bin"

INPUT="$ROOT_DIR/audio/input.m4a"
WAV="$ROOT_DIR/audio/input.wav"
OUTPUT="$ROOT_DIR/output/transcript"

mkdir -p "$ROOT_DIR/output/audio"

ffmpeg \
  -y \
  -i "$INPUT" \
  -ar 16000 \
  -ac 1 \
  -c:a pcm_s16le \
  "$WAV"

"$WHISPER_BIN" \
  --no-gpu \
  --no-timestamps \
  -m "$MODEL" \
  -f "$WAV" \
  -otxt \
  -of "$OUTPUT"

echo "Generated output/transcript.txt"
