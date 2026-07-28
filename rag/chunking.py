"""
Splits long documents (policy wordings, medical guidelines, regulatory
text) into smaller pieces before they get embedded. Simple sentence-aware
chunker - nothing fancy, just avoids cutting a sentence in half.
"""
import re


def chunk_text(text: str, max_chars: int = 800, overlap: int = 100) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) <= max_chars:
            current += (" " if current else "") + sentence
        else:
            if current:
                chunks.append(current)
            # start the next chunk with a bit of overlap from the end of the last one
            current = current[-overlap:] + " " + sentence if current else sentence

    if current:
        chunks.append(current)

    return chunks
