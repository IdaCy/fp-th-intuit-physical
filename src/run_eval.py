from __future__ import annotations

import argparse
import math
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv
from openai import OpenAI

from src.prompting import SYSTEM_PROMPT, build_user_prompt, parse_answer
from src.utils import CONFIGS_DIR, INTERIM_DIR, REPORTS_DIR, RESULTS_DIR, ensure_dirs


MODEL_PRICING_PER_1M = {
    "gpt-5-mini": {"input": 0.25, "output": 2.0},
    "gpt-5.4": {"input": 10.0, "output": 30.0},
}


def estimate_run_cost(df: pd.DataFrame, model: str, max_output_tokens: int) -> float:
    avg_input_tokens = df["vignette"].str.len().mean() / 4
    prompt_overhead = len(SYSTEM_PROMPT) / 4 + 20
    total_input_tokens = len(df) * (avg_input_tokens + prompt_overhead)
    total_output_tokens = len(df) * max_output_tokens
    pricing = MODEL_PRICING_PER_1M[model]
    return (total_input_tokens * pricing["input"] + total_output_tokens * pricing["output"]) / 1_000_000


def append_cost_note(model: str, estimated_cost: float) -> None:
    path = Path("private/cost_tracking.md")
    if not path.exists():
        raise RuntimeError("private/cost_tracking.md must exist before API calls")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a") as handle:
        handle.write(f"\n- planned eval for {model} at {timestamp}\n")
        handle.write(f"  estimated cost: ${estimated_cost:.4f}\n")


def append_actual_cost(model: str, input_tokens: int, output_tokens: int) -> None:
    pricing = MODEL_PRICING_PER_1M[model]
    actual_cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    path = Path("private/cost_tracking.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a") as handle:
        handle.write(f"- completed eval chunk for {model} at {timestamp}\n")
        handle.write(f"  actual input tokens: {input_tokens}\n")
        handle.write(f"  actual output tokens: {output_tokens}\n")
        handle.write(f"  actual cost: ${actual_cost:.4f}\n")


def call_model(client: OpenAI, model: str, user_prompt: str, temperature: float, max_output_tokens: int):
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
    output_tokens = getattr(usage, "output_tokens", 0) if usage else 0
    return response.output_text, input_tokens, output_tokens


def run_eval(model: str, limit: int | None = None) -> pd.DataFrame:
    load_dotenv()
    ensure_dirs()
    config = yaml.safe_load((CONFIGS_DIR / "eval.yaml").read_text())
    prepared = pd.read_csv(INTERIM_DIR / "prepared_physical_single_items.csv")
    if limit is not None:
        prepared = prepared.head(limit).copy()
    estimated_cost = estimate_run_cost(prepared, model, config["max_output_tokens"])
    append_cost_note(model, estimated_cost)

    if estimated_cost > 30:
        raise RuntimeError(f"Projected cost ${estimated_cost:.2f} exceeds the approval threshold")

    client = OpenAI()
    output_path = RESULTS_DIR / "model_outputs" / f"{model.replace('.', '_')}_predictions.csv"
    existing_rows: list[dict[str, object]]
    if output_path.exists():
        existing = pd.read_csv(output_path)
        done_ids = set(existing["item_instance_id"])
        prepared = prepared[~prepared["item_instance_id"].isin(done_ids)].copy()
        existing_rows = existing.to_dict("records")
    else:
        existing_rows = []

    total_input_tokens = 0
    total_output_tokens = 0
    new_rows: list[dict[str, object]] = []
    for _, row in prepared.iterrows():
        prompt = build_user_prompt(row["vignette"])
        raw_output, input_tokens, output_tokens = call_model(client, model, prompt, config["temperature"], config["max_output_tokens"])
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens
        parsed = parse_answer(raw_output)
        if parsed is None:
            raw_output, retry_input_tokens, retry_output_tokens = call_model(
                client,
                model,
                f"{prompt}\n\nReturn exactly one character: 1, 2, 3, or 4.",
                config["temperature"],
                config["max_output_tokens"],
            )
            total_input_tokens += retry_input_tokens
            total_output_tokens += retry_output_tokens
            parsed = parse_answer(raw_output)

        new_rows.append(
            {
                "model": model,
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
    append_actual_cost(model, total_input_tokens, total_output_tokens)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run_eval(args.model, limit=args.limit)


if __name__ == "__main__":
    main()
