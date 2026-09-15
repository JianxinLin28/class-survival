#!/bin/bash

# ./prompt.sh 4 means the whole Class4 folder
# ./prompt.sh 4 3 means Class 4 Slide 3

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

CLASS="${1:-4}"
SLIDE="$2"

CLASS_FOLDER="Class${CLASS}"

cd "$ROOT_DIR"

if [ -z "$SLIDE" ]; then
    INPUT_PATH="output/$CLASS_FOLDER"
else
    SLIDE_FILE=$(printf "Slides_%03d.png" "$SLIDE")
    INPUT_PATH="output/$CLASS_FOLDER/$SLIDE_FILE"
fi

python3 text_reader.py "$INPUT_PATH"
python3 prompt.py

echo "Generated output/prompt.txt"

