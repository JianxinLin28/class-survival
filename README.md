# Class Survival

This project helps with:

resizing/repositioning Zoom

capturing lecture slides

OCRing slides

transcribing Zoom/system audio

generating a GPT-ready prompt from slides + recent transcript context

Project Structure

```
Root/
├── .venv/
├── whisper.cpp/
│
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
└── output/
    ├── Class4/
    │   ├── Slide_001.png
    │   ├── Slide_002.png
    │   └── ...
    │
    ├── audio/
    │   └── chunks/
    │       ├── chunk_00000.wav
    │       ├── chunk_00000.txt
    │       ├── chunk_00001.wav
    │       ├── chunk_00001.txt
    │       └── ...
    │
    ├── text.txt
    ├── transcript.txt
    └── prompt.txt
```

1. Install Homebrew Dependencies

Install the required system tools:

brew install tesseract
brew install ffmpeg
brew install cmake

Install BlackHole:

brew install --cask blackhole-2ch

You may need to restart the Mac after installing BlackHole.

2. Create the Python Virtual Environment

From the Root folder:

python3 -m venv .venv

Install the Python dependencies:

./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt

requirements.txt:

Pillow
pytesseract

You can activate the venv manually if desired:

source .venv/bin/activate

This is not required for the normal shell scripts if they call .venv/bin/python directly.

3. Configure macOS Permissions

Open:

System Settings
→ Privacy & Security
→ Accessibility

Enable the application you use to run the scripts, such as:

Terminal
Visual Studio Code
iTerm

Also enable the same application under:

System Settings
→ Privacy & Security
→ Screen & System Audio Recording

After changing permissions, fully quit and reopen the application.

Test Accessibility access:

osascript -e 'tell application "System Events" to get name of every process'

4. Configure Zoom Resizing

Edit zoom_resize.py.

Example:

X = 0
Y = 0
WIDTH = 780
HEIGHT = 720

The script looks for:

Zoom Workplace

or:

zoom.us

5. Configure Screenshot Cropping

Edit screen_shot.py.

Example:

X = 0
Y = 300
BOTTOM = 50

WIDTH = 780
HEIGHT = 720 - Y - BOTTOM

Screenshots should be automatically numbered:

Slide_001.png
Slide_002.png
Slide_003.png

6. Make the Shell Scripts Executable

Run once:

chmod +x sh/capture.sh
chmod +x sh/prompt.sh
chmod +x sh/transcript.sh

7. Capture Slides

Capture a slide for Class 4:

./sh/capture.sh 4

This:

1. resizes/repositions Zoom
2. captures the configured screen region
3. saves the screenshot to output/Class4/

Example:

output/Class4/Slide_001.png

Running the same command again creates:

output/Class4/Slide_002.png

To use another class:

./sh/capture.sh 5

which saves into:

output/Class5/

8. OCR Slides and Generate a Prompt

Use the entire Class 4 folder:

./sh/prompt.sh 4

This OCRs every PNG inside:

output/Class4/

To use only one slide:

./sh/prompt.sh 4 3

This uses:

output/Class4/Slide_003.png

The OCR output is written to:

output/text.txt

The final GPT-ready prompt is written to:

output/prompt.txt

prompt.py also includes the most recent transcript chunks when available.

9. Install whisper.cpp

Clone it inside Root:

git clone https://github.com/ggml-org/whisper.cpp.git

Then:

cd whisper.cpp

Download the English base model:

sh ./models/download-ggml-model.sh base.en

10. Build whisper.cpp on This Mac

On this Intel Mac, the default Metal build hangs during initialization.

Build without Metal:

rm -rf build

cmake -B build \
  -DGGML_METAL=OFF

cmake --build build -j --config Release

Test it:

./build/bin/whisper-cli \
  --no-gpu \
  --no-timestamps \
  -m models/ggml-base.en.bin \
  -f samples/jfk.wav

Return to the project root:

cd ..

11. Configure BlackHole

Open:

Applications
→ Utilities
→ Audio MIDI Setup

If the Audio Devices window is not visible:

Window
→ Show Audio Devices

Click:

+
→ Create Multi-Output Device

Enable:

MacBook Pro Speakers
BlackHole 2ch

Recommended configuration:

Primary / Clock Source:
MacBook Pro Speakers

MacBook Pro Speakers:
Drift Correction OFF

BlackHole 2ch:
Drift Correction ON

Make sure both devices use the same sample rate, for example:

48,000 Hz

Then go to:

System Settings
→ Sound
→ Output

and select:

Multi-Output Device

This creates:

Zoom / system audio
        ↓
Multi-Output Device
        ├── MacBook Pro Speakers
        └── BlackHole 2ch

so you can hear the lecture while FFmpeg records it.

12. Verify BlackHole

List audio devices:

ffmpeg -f avfoundation -list_devices true -i ""

You should see something like:

AVFoundation audio devices:
[0] BlackHole 2ch
[1] MacBook Pro Microphone
...

The exact BlackHole device number may vary.

The script finds it automatically by name.

13. Test System Audio Capture

Record 10 seconds:

ffmpeg \
  -f avfoundation \
  -i ":0" \
  -t 10 \
  -ac 1 \
  -ar 16000 \
  -c:a pcm_s16le \
  test_blackhole.wav

Replace 0 if BlackHole has another device index.

Play Zoom or YouTube audio while recording.

Then:

open test_blackhole.wav

You should hear the captured system audio.

Test Whisper:

./whisper.cpp/build/bin/whisper-cli \
  --no-gpu \
  --no-timestamps \
  -m ./whisper.cpp/models/ggml-base.en.bin \
  -f test_blackhole.wav

14. Start Live Transcription

Run:

./sh/transcript.sh

The script:

1. finds BlackHole automatically
2. records system audio continuously
3. splits it into 10-second WAV chunks
4. transcribes completed chunks with whisper.cpp
5. appends transcript text to output/transcript.txt

Temporary chunks are stored under:

output/audio/chunks/

Example:

chunk_00000.wav
chunk_00000.txt
chunk_00001.wav
chunk_00001.txt
...

Press:

Ctrl+C

to stop.

15. Transcript Chunk Retention

Because 10-second chunks grow quickly, transcript.sh should keep only a limited rolling history.

For example:

MAX_CHUNKS=20

keeps approximately:

20 × 10 seconds = 200 seconds

or about 3 minutes 20 seconds of chunk history.

The full accumulated session transcript can still remain in:

output/transcript.txt

16. Prompt Transcript Context

prompt.py should read only the most recent transcript chunks.

Recommended:

MAX_TRANSCRIPT_CHUNKS = 5

With 10-second chunks, this gives approximately the most recent:

50 seconds

of professor audio.

Prompt priority is approximately:

1. Most recent professor transcript
2. Previous few transcript chunks
3. Last/current slide
4. Earlier slides

17. Normal Class Workflow

At the start of class:

./sh/transcript.sh

Leave it running in one terminal.

Whenever you want to capture a slide:

./sh/capture.sh 4

If you need help using all captured Class 4 slides:

./sh/prompt.sh 4

If you only want slide 3:

./sh/prompt.sh 4 3

Then open:

output/prompt.txt

and paste it into ChatGPT.

18. requirements.txt

Keep it minimal:

Pillow
pytesseract

Install:

./.venv/bin/python -m pip install -r requirements.txt

To inspect everything installed in the venv:

./.venv/bin/python -m pip freeze

19. Recommended .gitignore

.venv/
output/
whisper.cpp/
__pycache__/
*.pyc
.DS_Store
test_blackhole.wav

Quick Reference

Capture another Class 4 slide:

./sh/capture.sh 4

Generate a prompt from all Class 4 slides:

./sh/prompt.sh 4

Generate a prompt from Class 4, slide 3:

./sh/prompt.sh 4 3

Start live transcription:

./sh/transcript.sh

Install Python dependencies without activating the venv:

./.venv/bin/python -m pip install -r requirements.txt

Test OCR dependencies:

./.venv/bin/python -c "import pytesseract; from PIL import Image; print('OCR works')"

Test Whisper:

./whisper.cpp/build/bin/whisper-cli \
  --no-gpu \
  --no-timestamps \
  -m ./whisper.cpp/models/ggml-base.en.bin \
  -f test_blackhole.wav