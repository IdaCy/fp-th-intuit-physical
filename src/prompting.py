from __future__ import annotations

import re


PROMPT_VARIANTS = {
    "no_cot": {
        "system_prompt": "Answer the multiple-choice question with a single digit: 1, 2, 3, or 4.",
        "user_suffix": "Reply with only one digit: 1, 2, 3, or 4.",
        "retry_suffix": "Return exactly one character: 1, 2, 3, or 4.",
    },
    "cot": {
        "system_prompt": "Solve the multiple-choice question. You may reason briefly, but end with a final line in the format Final answer: <digit> where <digit> is 1, 2, 3, or 4.",
        "user_suffix": "Think through the vignette briefly if needed, then end with exactly one final line formatted as Final answer: 1, Final answer: 2, Final answer: 3, or Final answer: 4.",
        "retry_suffix": "Redo the answer and end with exactly one final line formatted as Final answer: 1, Final answer: 2, Final answer: 3, or Final answer: 4.",
    },
    "repeat": {
        "system_prompt": "Solve the multiple-choice question carefully and answer with a single digit: 1, 2, 3, or 4.",
        "user_suffix": "Read the question twice mentally before answering. Reply with only one digit: 1, 2, 3, or 4.",
        "retry_suffix": "Return exactly one character: 1, 2, 3, or 4.",
    },
}


def get_prompt_variant(condition: str) -> dict[str, str]:
    if condition not in PROMPT_VARIANTS:
        raise ValueError(f"Unknown prompt condition: {condition}")
    return PROMPT_VARIANTS[condition]


def build_user_prompt(vignette: str, condition: str = "no_cot") -> str:
    variant = get_prompt_variant(condition)
    if condition == "repeat":
        return f"{vignette.strip()}\n\nRead the same question again:\n\n{vignette.strip()}\n\n{variant['user_suffix']}"
    return f"{vignette.strip()}\n\n{variant['user_suffix']}"


def parse_answer(text: str) -> str | None:
    final_line = re.search(r"Final answer:\s*([1-4])", text, flags=re.I)
    if final_line:
        return final_line.group(1)
    match = re.search(r"\b([1-4])\b", text)
    if match:
        return match.group(1)
    stripped = text.strip()
    if stripped in {"1", "2", "3", "4"}:
        return stripped
    return None
