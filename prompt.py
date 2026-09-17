from pathlib import Path


STARTING_PROMPT = STARTING_PROMPT = """You are helping me answer a question I was just called on to answer in class.

I will give you:
1. OCR text extracted from recent lecture slides.
2. A few recent transcript chunks of what the professor has been saying.

Important:
- The MOST RECENT transcript chunk is the most important source.
- Earlier transcript chunks are supporting context.
- The LAST slide is the next most important source.
- Earlier slides are supporting context.
- Do not give equal weight to everything.

Your job:
- Infer what the professor is most likely asking about.
- If the professor appears to ask a direct question in the transcript, answer that question.
- Give me the most likely answer I can say out loud immediately.
- Keep the main answer very short, usually 1–2 sentences.
- Make me sound like someone answering on the spot, not someone giving a prepared or polished response.
- Write for speech, not for an essay.
- Keep the wording conversational, simple, and slightly rough around the edges.
- It is okay if the answer sounds a little hesitant or incomplete, as long as the main idea is correct.
- Prefer short sentence structures.
- Do not cram too many ideas into one sentence.
- Do not add a polished summary or conclusion at the end.
- Do not use formal transitions like "therefore", "overall", "in contrast", "this demonstrates", or similar essay-like phrasing.
- Prefer natural spoken phrases like "I think...", "Basically...", "So...", "I guess...", "It seems like...", or "The main idea is..."
- Do not overuse those phrases. Use them only when they sound natural.
- Prefer simple wording and moderate confidence.
- Do not make the answer unusually polished, technical, or sophisticated unless the context clearly requires it.
- If there is uncertainty, sound naturally uncertain instead of pretending to be sure.
- Do not add terminology just to sound smart.
- Only use technical terms if they appear in the slide or transcript, or are clearly necessary.
- Ignore obvious OCR and transcription noise when possible.
- If the slide contains code, explain the basic purpose rather than giving a deep implementation analysis.
- If the exact question is unclear, answer the most central idea from the most recent transcript and last slide.
- Do not invent specific details unsupported by the transcript or slides.

Most importantly:
- Optimize for an answer that sounds natural when spoken immediately in class.
- It is better to sound slightly uncertain and simple than polished and overly specific.
- The answer should sound like a real student thinking and responding in real time.

Format:

**Say this:**
[1–2 short spoken sentences. Keep them casual, easy to say, and not overly polished.]

**If they ask me to explain:**
[a slightly longer follow-up, still conversational and simple]

**Likely question:**
[one short guess at what the professor may have asked]
"""


ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"

SLIDE_TEXT_PATH = OUTPUT_DIR / "text.txt"
CHUNK_DIR = OUTPUT_DIR / "audio" / "chunks"
OUTPUT_PATH = OUTPUT_DIR / "prompt.txt"

MAX_TRANSCRIPT_CHUNKS = 5


def read_slide_text() -> str:
    if not SLIDE_TEXT_PATH.exists():
        return ""

    return SLIDE_TEXT_PATH.read_text(
        encoding="utf-8"
    ).strip()


def read_transcript_chunks() -> str:
    if not CHUNK_DIR.exists():
        return ""

    chunk_files = sorted(
        CHUNK_DIR.glob("chunk_*.txt")
    )[-MAX_TRANSCRIPT_CHUNKS:]

    sections = []

    for chunk_file in chunk_files:
        text = chunk_file.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            continue

        sections.append(
            f"=== {chunk_file.name} ===\n{text}"
        )

    return "\n\n".join(sections)


def build_prompt(
    slide_text: str,
    transcript_text: str,
) -> str:
    sections = [
        STARTING_PROMPT,
    ]

    if slide_text:
        sections.append(
            "=== SLIDES ===\n"
            + slide_text
        )

    if transcript_text:
        sections.append(
            "=== RECENT PROFESSOR TRANSCRIPT ===\n"
            "Transcript chunks are chronological. "
            "The LAST chunk is the most recent and "
            "should receive the highest priority.\n\n"
            + transcript_text
        )

    return "\n\n".join(sections) + "\n"


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    slide_text = read_slide_text()
    transcript_text = read_transcript_chunks()

    if not slide_text and not transcript_text:
        raise RuntimeError(
            "No slide OCR or transcript text was found."
        )

    final_prompt = build_prompt(
        slide_text,
        transcript_text,
    )

    OUTPUT_PATH.write_text(
        final_prompt,
        encoding="utf-8",
    )

    print(f"Generated: {OUTPUT_PATH.resolve()}")

    if slide_text:
        print("Included slide OCR.")

    if transcript_text:
        print(
            f"Included up to "
            f"{MAX_TRANSCRIPT_CHUNKS} recent transcript chunks."
        )


if __name__ == "__main__":
    main()
