import sys
import subprocess
from pathlib import Path


X = 0
Y = 300
BOTTOM = 50
WIDTH = 780
HEIGHT = 720-Y-BOTTOM
FOLDER_NAME = "Class3"
BASE_NAME = "Slide"

def get_next_filename(folder: Path) -> Path:
    index = 1

    while True:
        output = folder / f"{BASE_NAME}_{index:03}.png"

        if not output.exists():
            return output

        index += 1


def capture_region(
    x: int,
    y: int,
    width: int,
    height: int,
    output: Path,
):
    region = f"{x},{y},{width},{height}"

    subprocess.run(
        [
            "screencapture",
            "-x",
            "-R",
            region,
            str(output),
        ],
        check=True,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 screen_shot.py <folder>")
        return

    folder = Path(sys.argv[1])

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = get_next_filename(folder)

    capture_region(
        X,
        Y,
        WIDTH,
        HEIGHT,
        output,
    )

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
