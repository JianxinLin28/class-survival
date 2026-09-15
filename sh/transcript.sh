#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

WHISPER_DIR="$ROOT_DIR/whisper.cpp"
WHISPER_BIN="$WHISPER_DIR/build/bin/whisper-cli"
MODEL="$WHISPER_DIR/models/ggml-base.en.bin"

OUTPUT_DIR="$ROOT_DIR/output"
AUDIO_DIR="$OUTPUT_DIR/audio"
CHUNK_DIR="$AUDIO_DIR/chunks"
TRANSCRIPT="$OUTPUT_DIR/transcript.txt"

CHUNK_SECONDS=10
MAX_CHUNKS=10


# ------------------------------------------------------------
# Setup
# ------------------------------------------------------------

mkdir -p "$CHUNK_DIR"

# Start fresh every time transcript.sh runs
: > "$TRANSCRIPT"

echo "Starting new transcript session..."
echo "Transcript file cleared: $TRANSCRIPT"


# ------------------------------------------------------------
# Validate dependencies
# ------------------------------------------------------------

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "Error: ffmpeg is not installed."
    exit 1
fi

if [ ! -f "$WHISPER_BIN" ]; then
    echo "Error: whisper-cli not found:"
    echo "$WHISPER_BIN"
    exit 1
fi

if [ ! -f "$MODEL" ]; then
    echo "Error: Whisper model not found:"
    echo "$MODEL"
    exit 1
fi


# ------------------------------------------------------------
# Find BlackHole automatically
# ------------------------------------------------------------

DEVICE_LIST="$(
    ffmpeg \
        -hide_banner \
        -f avfoundation \
        -list_devices true \
        -i "" \
        2>&1 || true
)"

AUDIO_DEVICE="$(
    printf "%s\n" "$DEVICE_LIST" |
    sed -n 's/.*\[\([0-9][0-9]*\)\] BlackHole 2ch.*/\1/p' |
    head -n 1
)"

if [ -z "$AUDIO_DEVICE" ]; then
    echo "Error: Could not find BlackHole 2ch."
    echo
    echo "Available devices:"
    echo "$DEVICE_LIST"
    exit 1
fi

echo "Found BlackHole 2ch at audio device $AUDIO_DEVICE"


# ------------------------------------------------------------
# Clean previous temporary chunks
# ------------------------------------------------------------

rm -f "$CHUNK_DIR"/chunk_*.wav
rm -f "$CHUNK_DIR"/chunk_*.txt


# ------------------------------------------------------------
# Transcribe one completed chunk
# ------------------------------------------------------------

transcribe_chunk() {
    local index="$1"

    local number
    number=$(printf "%05d" "$index")

    local wav="$CHUNK_DIR/chunk_${number}.wav"
    local output_base="$CHUNK_DIR/chunk_${number}"
    local txt="${output_base}.txt"

    if [ ! -f "$wav" ]; then
        return
    fi

    "$WHISPER_BIN" \
        --no-gpu \
        --no-timestamps \
        --no-prints \
        -m "$MODEL" \
        -f "$wav" \
        -otxt \
        -of "$output_base"

    if [ ! -f "$txt" ]; then
        return
    fi

    local text
    text="$(cat "$txt")"

    if [ -z "$text" ]; then
        return
    fi

    echo "$text"
    echo "$text" >> "$TRANSCRIPT"
}


# ------------------------------------------------------------
# Ctrl+C handling
# ------------------------------------------------------------

STOP_REQUESTED=0

stop_transcription() {
    STOP_REQUESTED=1

    echo
    echo "Stop requested."
    echo "Finishing current audio chunk..."
}

trap stop_transcription INT TERM


# ------------------------------------------------------------
# Start continuous recording
#
# The subshell ignores Ctrl+C so FFmpeg itself doesn't get
# interrupted while writing a WAV. The parent shell handles
# Ctrl+C and stops FFmpeg at a safe chunk boundary instead.
# ------------------------------------------------------------

echo
echo "Listening..."
echo "Press Ctrl+C to stop."
echo
echo "Transcript:"
echo "----------------------------------------"

(
    trap '' INT

    exec ffmpeg \
        -hide_banner \
        -loglevel error \
        -nostdin \
        -f avfoundation \
        -i ":$AUDIO_DEVICE" \
        -ac 1 \
        -ar 16000 \
        -c:a pcm_s16le \
        -f segment \
        -segment_time "$CHUNK_SECONDS" \
        -reset_timestamps 1 \
        "$CHUNK_DIR/chunk_%05d.wav"
) &

FFMPEG_PID=$!

NEXT_CHUNK=0

cleanup_old_chunks() {
    local wav_files=("$CHUNK_DIR"/chunk_*.wav)

    # No matching files
    if [ ! -e "${wav_files[0]}" ]; then
        return
    fi

    local count=${#wav_files[@]}

    if [ "$count" -le "$MAX_CHUNKS" ]; then
        return
    fi

    local delete_count=$((count - MAX_CHUNKS))

    for ((i=0; i<delete_count; i++)); do
        local wav="${wav_files[$i]}"
        local base="${wav%.wav}"

        rm -f "$wav"
        rm -f "${base}.txt"
    done
}

# ------------------------------------------------------------
# Process completed chunks
#
# chunk N is considered complete once chunk N+1 exists.
# ------------------------------------------------------------

while true; do
    CURRENT_NUMBER=$(printf "%05d" "$NEXT_CHUNK")
    NEXT_NUMBER=$(printf "%05d" "$((NEXT_CHUNK + 1))")

    CURRENT_FILE="$CHUNK_DIR/chunk_${CURRENT_NUMBER}.wav"
    NEXT_FILE="$CHUNK_DIR/chunk_${NEXT_NUMBER}.wav"

    if [ -f "$CURRENT_FILE" ] && [ -f "$NEXT_FILE" ]; then
        echo
        echo "Audio chunk completed: chunk_${CURRENT_NUMBER}.wav"
        echo "Transcribing..."

        transcribe_chunk "$NEXT_CHUNK"

        echo "Finished: chunk_${CURRENT_NUMBER}.txt"

        cleanup_old_chunks

        NEXT_CHUNK=$((NEXT_CHUNK + 1))

        if [ "$STOP_REQUESTED" -eq 1 ]; then
            echo
            echo "Current chunk finished."
            echo "Stopping recorder..."

            kill -TERM "$FFMPEG_PID" 2>/dev/null || true
            break
        fi
    else
        sleep 0.5
    fi
done


# ------------------------------------------------------------
# Finish
# ------------------------------------------------------------

wait "$FFMPEG_PID" 2>/dev/null || true

echo
echo "----------------------------------------"
echo "Transcript saved to:"
echo "$TRANSCRIPT"
