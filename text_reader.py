import sys
from pathlib import Path

from PIL import Image, ImageOps
import pytesseract


ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_PATH = OUTPUT_DIR / "text.txt"

def read_text_from_png(image_path):
    image = Image.open(image_path)

    # Convert to grayscale
    image = ImageOps.grayscale(image)

    # Increase contrast / remove faint visual noise
    image = image.point(
        lambda p: 255 if p > 170 else 0
    )

    text = pytesseract.image_to_string(
        image,
        config="--psm 6",
    )

    return clean_text(text)


def clean_text(text: str) -> str:
    lines = []

    garbage = {
        "y",
        "yy",
        "//",
        "///",
        "{",
        "}",
        "|",
        "\\",
    }

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.lower() in garbage:
            continue

        # Remove single-character garbage
        if len(line) == 1 and not line.isdigit():
            continue

        lines.append(line)

    return "\n".join(lines)


def collect_text(input_path: Path) -> str:
    if input_path.is_file():
        if input_path.suffix.lower() != ".png":
            raise ValueError("Input file must be a PNG.")

        return read_text_from_png(input_path)

    if input_path.is_dir():
        png_files = sorted(input_path.glob("*.png"))

        if not png_files:
            raise FileNotFoundError(
                f"No PNG files found in: {input_path}"
            )

        sections = []

        for image_path in png_files:
            text = read_text_from_png(image_path)

            sections.append(
                f"=== {image_path.name} ===\n{text}"
            )

        return "\n\n".join(sections)

    raise ValueError("Input must be a PNG file or folder.")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 read_text.py <file-or-folder>")
        return

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Path does not exist: {input_path}")
        sys.exit(1)

    text = collect_text(input_path)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print(f"Saved OCR result to: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
