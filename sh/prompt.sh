#!/bin/bash

# Usage:
#   ./prompt.sh 4
#       → uses every slide in output/Class4/
#
#   ./prompt.sh 4 3
#       → uses output/Class4/Slide_003.png

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

PYTHON="$ROOT_DIR/.venv/bin/python"

CLASS="${1:-4}"
SLIDE="${2:-}"

CLASS_FOLDER="Class${CLASS}"
CLASS_PATH="$ROOT_DIR/output/$CLASS_FOLDER"


# ------------------------------------------------------------
# Validate Python environment
# ------------------------------------------------------------

if [ ! -x "$PYTHON" ]; then
    echo "Error: Python virtual environment not found:"
    echo "$PYTHON"
    echo
    echo "Create it with:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi


# ------------------------------------------------------------
# Resolve input
# ------------------------------------------------------------

if [ -z "$SLIDE" ]; then
    INPUT_PATH="$CLASS_PATH"

    if [ ! -d "$INPUT_PATH" ]; then
        echo "Error: Class folder not found:"
        echo "$INPUT_PATH"
        exit 1
    fi
else
    SLIDE_FILE=$(printf "Slide_%03d.png" "$SLIDE")
    INPUT_PATH="$CLASS_PATH/$SLIDE_FILE"

    if [ ! -f "$INPUT_PATH" ]; then
        echo "Error: Slide not found:"
        echo "$INPUT_PATH"
        exit 1
    fi
fi


# ------------------------------------------------------------
# Generate OCR text
# ------------------------------------------------------------

echo "Reading:"
echo "$INPUT_PATH"
echo

"$PYTHON" "$ROOT_DIR/text_reader.py" "$INPUT_PATH"


# ------------------------------------------------------------
# Generate final GPT prompt
# ------------------------------------------------------------

"$PYTHON" "$ROOT_DIR/prompt.py"


echo
echo "Generated:"
echo "$ROOT_DIR/output/prompt.txt"
