from __future__ import annotations

import json

import pandas as pd

from src.prompting import PROMPT_VARIANTS
from src.utils import INTERIM_DIR, RESULTS_DIR, ensure_dirs


def main() -> None:
    ensure_dirs()
    export_dir = RESULTS_DIR / "export"
    export_dir.mkdir(parents=True, exist_ok=True)

    prepared = pd.read_csv(INTERIM_DIR / "prepared_physical_single_items.csv")
    human = pd.read_csv(INTERIM_DIR / "human_item_time_stats.csv")
    merged = prepared.merge(human, on="item_instance_id", how="left")
    merged["estimated_time_horizon_minutes"] = (merged["median_rt_ms_all_valid"] / 1000 / 60).round(4)

    tasks = []
    for _, row in merged.iterrows():
        tasks.append(
            {
                "task_id": row["item_instance_id"],
                "task_name": row["template_id"],
                "task_description": f"INTUIT physical-only single-capability item in {row['base_context']}",
                "task_prompt": row["vignette"],
                "ground_truth_answer": int(row["correct_answer_number"]),
                "estimated_time_horizon_minutes": row["estimated_time_horizon_minutes"],
                "meta": {
                    "template_id": row["template_id"],
                    "counterbalance": int(row["counterbalance"]),
                    "base_context": row["base_context"],
                    "inference_level": row["inference_level"],
                    "condition": row["condition"],
                },
            }
        )
    (export_dir / "tasks.json").write_text(json.dumps(tasks, indent=2) + "\n")

    prompts = []
    for condition, prompt_data in PROMPT_VARIANTS.items():
        prompts.append(
            {
                "condition": condition,
                "system_prompt": prompt_data["system_prompt"],
                "user_suffix": prompt_data["user_suffix"],
                "retry_suffix": prompt_data["retry_suffix"],
            }
        )
    (export_dir / "prompts.json").write_text(json.dumps(prompts, indent=2) + "\n")

    item_level = pd.read_csv(RESULTS_DIR / "tables" / "item_level_results.csv")
    records = item_level[
        [
            "model",
            "condition",
            "item_instance_id",
            "parsed_prediction",
            "parse_failed",
            "correct_answer_number",
            "model_correct",
            "human_median_seconds_all_valid",
            "time_bin",
            "base_context",
        ]
    ].to_dict("records")
    (export_dir / "results.json").write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    main()
