# CS571 Class Helper Setup

This project provides a small workflow for:

* resizing/repositioning the Zoom window
* capturing lecture slides
* OCRing screenshots
* generating a GPT-ready prompt
* transcribing lecture audio locally with `whisper.cpp`

The intended project structure is:

```text
CS571/
├── zoom_resize.py
├── screen_shot.py
├── text_reader.py
├── prompt.py
├── requirements.txt
│
├── sh/
│   ├── capture.sh
│   ├── prompt.sh
│   └── transcript.sh
│
├── output/
│   ├── Class4/
│   │   ├── Slides_001.png
│   │   ├── Slides_002.png
│   │   └── ...
│   ├── audio/
│   ├── text.txt
│   ├── prompt.txt
│   └── transcript.txt
│
└── whisper.cpp/
```

## 1. Install Homebrew dependencies

Install Tesseract, FFmpeg, CMake, and BlackHole:

```bash
brew install tesseract ffmpeg cmake
brew install --cask blackhole-2ch
```

BlackHole may require a reboot after installation.

Tesseract is used for slide OCR.

FFmpeg is used for converting audio into a format Whisper can process.

BlackHole allows macOS system audio, including Zoom audio, to be routed into a recording/transcription workflow.

## 2. Create the Python virtual environment

From the `CS571` directory:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The `requirements.txt` file should contain:

```text
Pillow
pytesseract
```

The transcription system does not use the Python Whisper package.

## 3. Configure macOS permissions

The project needs macOS permission to manipulate Zoom and capture the screen.

Open:

```text
System Settings
→ Privacy & Security
→ Accessibility
```

Enable the application that runs the scripts, such as:

```text
Terminal
Visual Studio Code
iTerm
```

Also open:

```text
System Settings
→ Privacy & Security
→ Screen & System Audio Recording
```

and enable the same application.

Completely quit and reopen the application after changing permissions.

You can test Accessibility access with:

```bash
osascript -e 'tell application "System Events" to get name of every process'
```

## 4. Configure Zoom positioning

`zoom_resize.py` controls the Zoom window position and dimensions.

Example configuration:

```python
X = 0
Y = 0
WIDTH = 780
HEIGHT = 720
```

The script searches for either:

```text
Zoom Workplace
```

or:

```text
zoom.us
```

and resizes the front Zoom window.

## 5. Configure screenshot cropping

`screen_shot.py` controls which part of the screen becomes the slide screenshot.

Example:

```python
X = 0
Y = 300
BOTTOM = 50
WIDTH = 780
HEIGHT = 720 - Y - BOTTOM
```

The screenshot script automatically generates names such as:

```text
Slides_001.png
Slides_002.png
Slides_003.png
```

without overwriting previous screenshots.

## 6. Configure `capture.sh`

The capture command takes a class number.

Example:

```bash
./sh/capture.sh 4
```

This should:

```text
1. resize/reposition Zoom
2. take a screenshot
3. save it under output/Class4/
```

Example `capture.sh`:

```bash
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

CLASS="${1:-4}"
FOLDER="Class${CLASS}"

cd "$ROOT_DIR"

python3 zoom_resize.py
python3 screen_shot.py "output/$FOLDER"
```

Make it executable:

```bash
chmod +x sh/capture.sh
```

Example:

```bash
./sh/capture.sh 4
```

produces:

```text
output/Class4/Slides_001.png
```

Running it again produces:

```text
output/Class4/Slides_002.png
```

## 7. OCR screenshots

`text_reader.py` accepts either:

* an individual PNG
* an entire directory containing PNGs

Examples:

```bash
python3 text_reader.py output/Class4
```

or:

```bash
python3 text_reader.py output/Class4/Slides_003.png
```

The OCR result is always written to:

```text
output/text.txt
```

The script performs grayscale conversion and thresholding before sending the image to Tesseract.

It also removes some common OCR garbage.

## 8. Configure `prompt.sh`

`prompt.sh` accepts:

```text
CLASS
```

or:

```text
CLASS SLIDE
```

For example:

```bash
./sh/prompt.sh 4
```

OCRs all screenshots in:

```text
output/Class4/
```

while:

```bash
./sh/prompt.sh 4 3
```

only OCRs:

```text
output/Class4/Slides_003.png
```

Example `prompt.sh`:

```bash
#!/bin/bash

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
```

Make it executable:

```bash
chmod +x sh/prompt.sh
```

The final GPT-ready prompt is written to:

```text
output/prompt.txt
```

## 9. Install `whisper.cpp`

From the `CS571` directory:

```bash
git clone https://github.com/ggml-org/whisper.cpp.git
```

Enter it:

```bash
cd whisper.cpp
```

Download the English base model:

```bash
sh ./models/download-ggml-model.sh base.en
```

The official project provides this model-download helper and uses CMake for its normal build flow.

## 10. Build Whisper on this Intel Mac

On this machine, the normal Metal build hangs during initialization.

Build `whisper.cpp` with Metal disabled:

```bash
rm -rf build

cmake -B build \
  -DGGML_METAL=OFF

cmake --build build -j --config Release
```

`GGML_METAL` is enabled by default on Apple platforms, so explicitly disabling it forces the CPU-oriented build used here.

Test it with the included sample:

```bash
./build/bin/whisper-cli \
  -m models/ggml-base.en.bin \
  -f samples/jfk.wav
```

If this generates a transcript, Whisper is working.

## 11. Convert audio for Whisper

`whisper-cli` expects compatible audio such as a 16-bit WAV.

For a Voice Memo or other `.m4a` file:

```bash
ffmpeg \
  -i input.m4a \
  -ar 16000 \
  -ac 1 \
  -c:a pcm_s16le \
  output.wav
```

This converts the recording to:

```text
16 kHz
mono
16-bit PCM WAV
```

which matches the conversion recommended by the `whisper.cpp` project.

You can then transcribe it with:

```bash
./whisper.cpp/build/bin/whisper-cli \
  --no-gpu \
  --no-timestamps \
  -m ./whisper.cpp/models/ggml-base.en.bin \
  -f output.wav
```

## 12. Configure BlackHole for Zoom audio

BlackHole allows system audio to be routed into another application while still allowing you to hear it.

After installing BlackHole, open:

```text
Applications
→ Utilities
→ Audio MIDI Setup
```

Click:

```text
+
→ Create Multi-Output Device
```

Enable:

```text
your headphones/speakers
BlackHole 2ch
```

Use your normal speakers/headphones as the main clock source.

Enable:

```text
Drift Correction
```

for BlackHole.

Then select the Multi-Output Device as the Mac's sound output.

This sends audio simultaneously to your headphones/speakers and BlackHole.

## 13. Identify BlackHole's FFmpeg device

Run:

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

Look under the audio devices for:

```text
BlackHole 2ch
```

Note its device number.

That device can then be used by FFmpeg to record Zoom/system audio.

## 14. Transcription workflow

The intended audio pipeline is:

```text
Zoom
  ↓
Multi-Output Device
  ├── headphones/speakers
  └── BlackHole 2ch
          ↓
        FFmpeg
          ↓
        WAV
          ↓
     whisper.cpp
          ↓
output/transcript.txt
```

A `transcript.sh` script can hide all of the FFmpeg and Whisper arguments so the normal workflow only requires one command.

## 15. Normal class workflow

Capture slides whenever useful:

```bash
./sh/capture.sh 4
```

Run it repeatedly:

```text
output/Class4/Slides_001.png
output/Class4/Slides_002.png
output/Class4/Slides_003.png
...
```

If you want GPT context from the entire class screenshot folder:

```bash
./sh/prompt.sh 4
```

If you only want slide 3:

```bash
./sh/prompt.sh 4 3
```

The result is:

```text
output/prompt.txt
```

which can be pasted directly into ChatGPT.

## 16. Git setup

Recommended `.gitignore`:

```gitignore
.venv/
output/
whisper.cpp/
__pycache__/
*.pyc
.DS_Store
```

`whisper.cpp/` is excluded because it is its own Git repository.

Then:

```bash
git add .
git commit -m "Add class capture and prompt helper"
git push
```

## Quick reference

Capture another slide from Class 4:

```bash
./sh/capture.sh 4
```

Generate a prompt from all Class 4 slides:

```bash
./sh/prompt.sh 4
```

Generate a prompt from only Class 4 slide 3:

```bash
./sh/prompt.sh 4 3
```

Activate Python manually if needed:

```bash
source .venv/bin/activate
```

Test Whisper:

```bash
./whisper.cpp/build/bin/whisper-cli \
  --no-gpu \
  --no-timestamps \
  -m ./whisper.cpp/models/ggml-base.en.bin \
  -f test.wav
```

The goal is that all the ugly setup happens once. During class, the commands you actually need to remember should stay very small.
