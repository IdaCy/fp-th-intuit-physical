from __future__ import annotations

import argparse
import math
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv
from openai import OpenAI

from src.prompting import build_user_prompt, get_prompt_variant, parse_answer
from src.utils import CONFIGS_DIR, INTERIM_DIR, REPORTS_DIR, RESULTS_DIR, ensure_dirs


MODEL_PRICING_PER_1M = {
    "gpt-5-mini": {"input": 0.25, "output": 2.0},
    "gpt-5.4": {"input": 10.0, "output": 30.0},
    "gpt-4.1": {"input": 2.0, "output": 8.0},
}

MODEL_REASONING = {
    "gpt-5-mini": "minimal",
    "gpt-5.4": "none",
    "gpt-4.1": None,
}

MODEL_REASONING_BY_CONDITION = {
    "no_cot": {
        "gpt-5-mini": "minimal",
        "gpt-5.4": "none",
        "gpt-4.1": None,
    },
    "cot": {
        "gpt-5-mini": "medium",
        "gpt-5.4": "medium",
        "gpt-4.1": None,
    },
    "repeat": {
        "gpt-5-mini": "minimal",
        "gpt-5.4": "none",
        "gpt-4.1": None,
    },
}

MODEL_VERBOSITY = {
    "gpt-5-mini": "low",
    "gpt-5.4": "low",
    "gpt-4.1": "medium",
}


def estimate_run_cost(df: pd.DataFrame, model: str, max_output_tokens: int, condition: str) -> float:
    avg_input_tokens = df["vignette"].str.len().mean() / 4
    variant = get_prompt_variant(condition)
    prompt_overhead = (len(variant["system_prompt"]) + len(variant["user_suffix"])) / 4 + 20
    if condition == "repeat":
        prompt_overhead += avg_input_tokens
    total_input_tokens = len(df) * (avg_input_tokens + prompt_overhead)
    total_output_tokens = len(df) * max_output_tokens
    pricing = MODEL_PRICING_PER_1M[model]
    return (total_input_tokens * pricing["input"] + total_output_tokens * pricing["output"]) / 1_000_000


def append_cost_note(model: str, condition: str, estimated_cost: float) -> None:
    path = Path("private/cost_tracking.md")
    if not path.exists():
        raise RuntimeError("private/cost_tracking.md must exist before API calls")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a") as handle:
        handle.write(f"\n- planned eval for {model} [{condition}] at {timestamp}\n")
        handle.write(f"  estimated cost: ${estimated_cost:.4f}\n")


def append_actual_cost(model: str, condition: str, input_tokens: int, output_tokens: int) -> None:
    pricing = MODEL_PRICING_PER_1M[model]
    actual_cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    path = Path("private/cost_tracking.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a") as handle:
        handle.write(f"- completed eval chunk for {model} [{condition}] at {timestamp}\n")
        handle.write(f"  actual input tokens: {input_tokens}\n")
        handle.write(f"  actual output tokens: {output_tokens}\n")
        handle.write(f"  actual cost: ${actual_cost:.4f}\n")


def output_filename(model: str, condition: str) -> str:
    base = model.replace(".", "_")
    if condition == "no_cot":
        return f"{base}_predictions.csv"
    return f"{base}__{condition}_predictions.csv"


def call_model(client: OpenAI, model: str, condition: str, user_prompt: str, max_output_tokens: int):
    variant = get_prompt_variant(condition)
    request = {
        "model": model,
        "input": [
            {"role": "system", "content": variant["system_prompt"]},
            {"role": "user", "content": user_prompt},
        ],
        "text": {"verbosity": MODEL_VERBOSITY.get(model, "low")},
        "max_output_tokens": max_output_tokens,
    }
    reasoning_effort = MODEL_REASONING_BY_CONDITION.get(condition, MODEL_REASONING).get(model)
    if reasoning_effort is not None:
        request["reasoning"] = {"effort": reasoning_effort}

    response = client.responses.create(
        **request
    )
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
    output_tokens = getattr(usage, "output_tokens", 0) if usage else 0
    return response.output_text, input_tokens, output_tokens


def run_eval(model: str, condition: str = "no_cot", limit: int | None = None) -> pd.DataFrame:
    load_dotenv()
    ensure_dirs()
    config = yaml.safe_load((CONFIGS_DIR / "eval.yaml").read_text())
    prepared = pd.read_csv(INTERIM_DIR / "prepared_physical_single_items.csv")
    if limit is not None:
        prepared = prepared.head(limit).copy()
    estimated_cost = estimate_run_cost(prepared, model, config["max_output_tokens"], condition)
    append_cost_note(model, condition, estimated_cost)

    if estimated_cost > 30:
        raise RuntimeError(f"Projected cost ${estimated_cost:.2f} exceeds the approval threshold")

    client = OpenAI()
    output_path = RESULTS_DIR / "model_outputs" / output_filename(model, condition)
    existing_rows: list[dict[str, object]]
    if output_path.exists():
        existing = pd.read_csv(output_path)
        successful = existing[existing["parsed_prediction"].notna()].copy()
        done_ids = set(successful["item_instance_id"])
        prepared = prepared[~prepared["item_instance_id"].isin(done_ids)].copy()
        existing_rows = successful.to_dict("records")
    else:
        existing_rows = []

    total_input_tokens = 0
    total_output_tokens = 0
    new_rows: list[dict[str, object]] = []
    variant = get_prompt_variant(condition)
    for _, row in prepared.iterrows():
        prompt = build_user_prompt(row["vignette"], condition=condition)
        raw_output, input_tokens, output_tokens = call_model(client, model, condition, prompt, config["max_output_tokens"])
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens
        parsed = parse_answer(raw_output)
        if parsed is None:
            raw_output, retry_input_tokens, retry_output_tokens = call_model(
                client,
                model,
                condition,
                f"{prompt}\n\n{variant['retry_suffix']}",
                config["max_output_tokens"],
            )
            total_input_tokens += retry_input_tokens
            total_output_tokens += retry_output_tokens
            parsed = parse_answer(raw_output)

        new_rows.append(
            {
                "model": model,
                "condition": condition,
                "item_instance_id": row["item_instance_id"],
                "template_id": row["template_id"],
                "counterbalance": row["counterbalance"],
                "raw_prediction": raw_output.strip(),
                "parsed_prediction": parsed,
                "parse_failed": int(parsed is None),
                "correct_answer_number": int(row["correct_answer_number"]),
                "model_correct": int(parsed == str(int(row["correct_answer_number"]))) if parsed is not None else math.nan,
            }
        )

    output = pd.DataFrame(existing_rows + new_rows)
    output.to_csv(output_path, index=False)
    append_actual_cost(model, condition, total_input_tokens, total_output_tokens)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--condition", default="no_cot")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run_eval(args.model, condition=args.condition, limit=args.limit)


if __name__ == "__main__":
    main()
