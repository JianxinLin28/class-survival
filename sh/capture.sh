#!/bin/bash

# Usage:
#   ./capture.sh 4
#       → saves into output/Class4/

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

PYTHON="$ROOT_DIR/.venv/bin/python"

CLASS="${1:-4}"
FOLDER="Class${CLASS}"
OUTPUT_PATH="$ROOT_DIR/output/$FOLDER"


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
# Prepare output folder
# ------------------------------------------------------------

mkdir -p "$OUTPUT_PATH"


# ------------------------------------------------------------
# Resize Zoom
# ------------------------------------------------------------

"$PYTHON" "$ROOT_DIR/zoom_resize.py"


# ------------------------------------------------------------
# Capture slide
# ------------------------------------------------------------

"$PYTHON" "$ROOT_DIR/screen_shot.py" "$OUTPUT_PATH"


echo
echo "Capture saved under:"
echo "$OUTPUT_PATH"
