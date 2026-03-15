from __future__ import annotations

import re


SYSTEM_PROMPT = "Answer the multiple-choice question with a single digit: 1, 2, 3, or 4."


def build_user_prompt(vignette: str) -> str:
    return f"{vignette.strip()}\n\nReply with only one digit: 1, 2, 3, or 4."


def parse_answer(text: str) -> str | None:
    match = re.search(r"\b([1-4])\b", text)
    if match:
        return match.group(1)
    stripped = text.strip()
    if stripped in {"1", "2", "3", "4"}:
        return stripped
    return None
