"""Text cleaning helpers."""

from __future__ import annotations

import re


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def clean_text(text: str) -> str:
    ascii_text = text.encode("ascii", "ignore").decode("ascii")
    return normalize_whitespace(ascii_text)

