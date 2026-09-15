from pathlib import Path


STARTING_PROMPT = """You are helping me answer a question I was just called on to answer in class.

I will give you OCR text extracted from several recent lecture slides.

Important:
- The LAST slide is the most important.
- Assume the professor's question is most likely about the concept, example, code, claim, or comparison shown on the last slide.
- Use earlier slides mainly as supporting context.
- Do not give equal weight to every slide.

Your job:
- Infer what the professor is most likely asking about.
- Give me the most likely answer I can say out loud immediately.
- Keep the main answer very short, usually 1–2 sentences.
- Make me sound like a normal student who understands the general idea, not an expert.
- Prefer simple wording and moderate confidence.
- Do not make the answer unusually polished, technical, or sophisticated unless the slide clearly requires it.
- If there is uncertainty, use natural phrasing like "I think the idea is..." or "Basically..." instead of pretending to be completely certain.
- Do not add extra terminology just to sound smart.
- Ignore obvious OCR noise and reconstruct the intended slide content when possible.
- If the last slide contains code, explain the basic purpose rather than giving a deep implementation analysis.
- If the exact question is unclear, answer the most central point of the last slide.
- Do not invent specific details unsupported by the slides.

Most importantly: optimize for an answer that is reasonably correct and safe to say in class. It is better to sound slightly uncertain than confidently give an overly specific wrong answer.

Format:

**Say this:**
[a short, natural answer I can immediately say out loud]

**If they ask me to explain:**
[a slightly longer but still simple follow-up]

**Likely question:**
[one short guess at what the professor may have asked]

Here are the recent slides, in chronological order. The final slide should receive the highest priority:
"""

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"

INPUT_PATH = OUTPUT_DIR / "text.txt"
OUTPUT_PATH = OUTPUT_DIR / "prompt.txt"

def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_PATH}"
        )

    slide_text = INPUT_PATH.read_text(
        encoding="utf-8"
    ).strip()

    final_prompt = (
        STARTING_PROMPT
        + "\n\n"
        + slide_text
        + "\n"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        final_prompt,
        encoding="utf-8",
    )

    print(f"Generated: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
