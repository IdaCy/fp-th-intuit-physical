from __future__ import annotations

import math

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

from src.utils import INTERIM_DIR, RESULTS_DIR, ensure_dirs


def wilson_bounds(successes: int, total: int) -> tuple[float, float]:
    if total == 0:
        return (math.nan, math.nan)
    low, high = proportion_confint(successes, total, method="wilson")
    return float(low), float(high)


def label_time_bins(values: pd.Series, bin_count: int = 4) -> pd.Series:
    ranked = values.rank(method="first")
    bins = pd.qcut(ranked, q=bin_count, labels=False) + 1
    return bins.astype(int)


def main() -> None:
    ensure_dirs()
    prepared = pd.read_csv(INTERIM_DIR / "prepared_physical_single_items.csv")
    human = pd.read_csv(INTERIM_DIR / "human_item_time_stats.csv")
    merged = prepared.merge(human, on="item_instance_id", how="left")
    merged["human_median_seconds_all_valid"] = merged["median_rt_ms_all_valid"] / 1000
    merged["human_median_seconds_correct_valid"] = merged["median_rt_ms_correct_valid"] / 1000
    merged["time_bin"] = label_time_bins(merged["median_rt_ms_all_valid"])

    model_paths = sorted((RESULTS_DIR / "model_outputs").glob("*_predictions.csv"))
    model_frames = [pd.read_csv(path) for path in model_paths]
    all_results = pd.concat(model_frames, ignore_index=True)
    item_level = all_results.merge(merged, on=["item_instance_id", "template_id", "counterbalance", "correct_answer_number"], how="left")
    item_level.to_csv(RESULTS_DIR / "tables" / "item_level_results.csv", index=False)

    benchmark_size = pd.DataFrame(
        [
            {
                "physical_templates": int(merged["template_id"].nunique()),
                "physical_item_instances": int(merged["item_instance_id"].nunique()),
                "base_contexts": int(merged["base_context"].nunique()),
                "human_participants": int(pd.read_csv(INTERIM_DIR / "human_trials_physical_single.csv")["participant_id"].nunique()),
            }
        ]
    )
    benchmark_size.to_csv(RESULTS_DIR / "tables" / "benchmark_size.csv", index=False)

    overall_rows = []
    for model, group in item_level.groupby("model"):
        total = group["model_correct"].notna().sum()
        successes = int(group["model_correct"].sum())
        low, high = wilson_bounds(successes, total)
        overall_rows.append(
            {
                "model": model,
                "items": total,
                "accuracy": successes / total,
                "ci_low": low,
                "ci_high": high,
                "parse_failures": int(group["parse_failed"].sum()),
            }
        )
    overall = pd.DataFrame(overall_rows).sort_values("model")
    overall.to_csv(RESULTS_DIR / "tables" / "overall_accuracy.csv", index=False)

    bin_rows = []
    for (model, time_bin), group in item_level.groupby(["model", "time_bin"]):
        total = group["model_correct"].notna().sum()
        successes = int(group["model_correct"].sum())
        low, high = wilson_bounds(successes, total)
        bin_rows.append(
            {
                "model": model,
                "time_bin": int(time_bin),
                "items": total,
                "accuracy": successes / total,
                "ci_low": low,
                "ci_high": high,
                "median_human_seconds": group["human_median_seconds_all_valid"].median(),
            }
        )
    by_time = pd.DataFrame(bin_rows).sort_values(["model", "time_bin"])
    by_time.to_csv(RESULTS_DIR / "tables" / "accuracy_by_time_bin.csv", index=False)

    category_rows = []
    for (model, category), group in item_level.groupby(["model", "base_context"]):
        total = group["model_correct"].notna().sum()
        successes = int(group["model_correct"].sum())
        low, high = wilson_bounds(successes, total)
        category_rows.append(
            {
                "model": model,
                "base_context": category,
                "items": total,
                "accuracy": successes / total,
                "ci_low": low,
                "ci_high": high,
            }
        )
    by_category = pd.DataFrame(category_rows).sort_values(["model", "base_context"])
    by_category.to_csv(RESULTS_DIR / "tables" / "accuracy_by_base_context.csv", index=False)

    human_rows = []
    for time_bin, group in merged.groupby("time_bin"):
        human_rows.append(
            {
                "time_bin": int(time_bin),
                "items": int(group["item_instance_id"].nunique()),
                "median_human_seconds": group["human_median_seconds_all_valid"].median(),
                "median_human_accuracy": group["human_accuracy"].median(),
            }
        )
    pd.DataFrame(human_rows).sort_values("time_bin").to_csv(RESULTS_DIR / "tables" / "human_by_time_bin.csv", index=False)

    human_by_context = (
        merged.groupby("base_context", as_index=False)
        .agg(
            items=("item_instance_id", "nunique"),
            mean_human_accuracy=("human_accuracy", "mean"),
            median_human_seconds=("human_median_seconds_all_valid", "median"),
        )
        .sort_values("base_context")
    )
    human_by_context.to_csv(RESULTS_DIR / "tables" / "human_by_base_context.csv", index=False)


if __name__ == "__main__":
    main()
