#!/bin/bash

# ./capture.sh 4 means to put in Class4 folder

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

CLASS="${1:-4}"
FOLDER="Class${CLASS}"

cd "$ROOT_DIR"

python3 zoom_resize.py
python3 screen_shot.py "output/$FOLDER"
