import sys
from pathlib import Path

from PIL import Image, ImageOps
import pytesseract


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_PATH = OUTPUT_DIR / "text.txt"

MAX_SLIDES = 5


# ------------------------------------------------------------
# OCR one image
# ------------------------------------------------------------

def read_text_from_png(image_path: Path) -> str:
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


# ------------------------------------------------------------
# Clean OCR output
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Collect PNG files from folder
# ------------------------------------------------------------

def get_recent_png_files(
    input_path: Path,
    max_slides: int,
) -> list[Path]:

    png_files = sorted(
        input_path.glob("*.png")
    )

    if not png_files:
        raise FileNotFoundError(
            f"No PNG files found in: {input_path}"
        )

    # Only keep the most recent slides.
    return png_files[-max_slides:]


# ------------------------------------------------------------
# Collect OCR text
# ------------------------------------------------------------

def collect_text(input_path: Path) -> str:

    # --------------------------------------------------------
    # Single slide
    # --------------------------------------------------------

    if input_path.is_file():
        if input_path.suffix.lower() != ".png":
            raise ValueError(
                "Input file must be a PNG."
            )

        print(
            f"Reading slide: {input_path.name}"
        )

        return read_text_from_png(
            input_path
        )

    # --------------------------------------------------------
    # Folder of slides
    # --------------------------------------------------------

    if input_path.is_dir():

        png_files = get_recent_png_files(
            input_path,
            MAX_SLIDES,
        )

        print(
            f"Using {len(png_files)} "
            f"most recent slide(s):"
        )

        for image_path in png_files:
            print(
                f"  - {image_path.name}"
            )

        print()

        sections = []

        for image_path in png_files:
            print(
                f"OCR: {image_path.name}"
            )

            text = read_text_from_png(
                image_path
            )

            sections.append(
                f"=== {image_path.name} ===\n"
                f"{text}"
            )

        return "\n\n".join(
            sections
        )

    raise ValueError(
        "Input must be a PNG file or folder."
    )


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  python3 text_reader.py "
            "<file-or-folder>"
        )
        sys.exit(1)

    input_path = Path(
        sys.argv[1]
    )

    if not input_path.exists():
        print(
            f"Path does not exist: "
            f"{input_path}"
        )
        sys.exit(1)

    try:
        text = collect_text(
            input_path
        )

    except Exception as error:
        print(
            f"Error: {error}"
        )
        sys.exit(1)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        text,
        encoding="utf-8",
    )

    print()
    print(
        "Saved OCR result to:"
    )
    print(
        OUTPUT_PATH.resolve()
    )


if __name__ == "__main__":
    main()