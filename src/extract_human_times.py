from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils import INTERIM_DIR, RAW_DIR, RESULTS_DIR, ensure_dirs, normalize_template_id


RT_PARTICIPANT_THRESHOLD_MS = 20_000
RT_TRIAL_THRESHOLD_MS = 5_000


def load_and_clean_human_trials() -> pd.DataFrame:
    raw = pd.read_csv(RAW_DIR / "osf_results" / "paper_results" / "human_data_single_clean.csv")
    trials = raw[(raw["Display"] == "Trial") & (raw["Screen"] == "vignette")].copy()
    trials["template_id"] = trials["Spreadsheet: id"].map(normalize_template_id)
    trials["participant_id"] = trials["Participant Private ID"]
    trials["counterbalance"] = trials["Store: condition"].astype(int)
    trials["reaction_time_ms"] = trials["Reaction Time"]
    trials["human_correct"] = trials["Correct"]
    trials["human_response"] = trials["Response"]

    failed_attention = set(
        trials[(trials["template_id"] == "attention_check") & (trials["human_correct"] == 0)]["participant_id"].unique()
    )
    participant_medians = trials.groupby("participant_id")["reaction_time_ms"].median()
    fast_participants = set(participant_medians[participant_medians < RT_PARTICIPANT_THRESHOLD_MS].index)
    excluded = failed_attention | fast_participants

    trials = trials[~trials["participant_id"].isin(excluded)].copy()
    trials = trials[trials["template_id"] != "attention_check"].copy()
    trials["valid_trial"] = trials["reaction_time_ms"] >= RT_TRIAL_THRESHOLD_MS
    trials["item_instance_id"] = trials["template_id"] + "__c" + trials["counterbalance"].astype(str)
    return trials


def summarize_human_times(trials: pd.DataFrame, prepared: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    subset = trials[trials["item_instance_id"].isin(prepared["item_instance_id"])].copy()
    valid = subset[subset["valid_trial"]].copy()
    correct_valid = valid[valid["human_correct"] == 1].copy()

    summary = (
        subset.groupby("item_instance_id", as_index=False)
        .agg(
            human_attempts_total=("participant_id", "size"),
            human_participants=("participant_id", "nunique"),
            valid_attempts=("valid_trial", "sum"),
        )
        .merge(
            valid.groupby("item_instance_id", as_index=False).agg(
                human_accuracy=("human_correct", "mean"),
                median_rt_ms_all_valid=("reaction_time_ms", "median"),
                mean_rt_ms_all_valid=("reaction_time_ms", "mean"),
            ),
            on="item_instance_id",
            how="left",
        )
        .merge(
            correct_valid.groupby("item_instance_id", as_index=False).agg(
                median_rt_ms_correct_valid=("reaction_time_ms", "median")
            ),
            on="item_instance_id",
            how="left",
        )
        .sort_values("item_instance_id")
    )
    summary["human_accuracy"] = summary["human_accuracy"].round(4)
    return subset, summary


def write_outputs(trials: pd.DataFrame, summary: pd.DataFrame) -> None:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    trials.to_csv(INTERIM_DIR / "human_trials_physical_single.csv", index=False)
    summary.to_csv(INTERIM_DIR / "human_item_time_stats.csv", index=False)

    overall = pd.DataFrame(
        [
            {
                "included_item_instances": int(summary["item_instance_id"].nunique()),
                "included_participants": int(trials["participant_id"].nunique()),
                "all_valid_median_seconds_median": round(summary["median_rt_ms_all_valid"].median() / 1000, 3),
                "all_valid_median_seconds_min": round(summary["median_rt_ms_all_valid"].min() / 1000, 3),
                "all_valid_median_seconds_max": round(summary["median_rt_ms_all_valid"].max() / 1000, 3),
                "correct_only_median_seconds_median": round(summary["median_rt_ms_correct_valid"].median() / 1000, 3),
            }
        ]
    )
    overall.to_csv(RESULTS_DIR / "tables" / "human_timing_summary.csv", index=False)


def main() -> None:
    ensure_dirs()
    prepared = pd.read_csv(INTERIM_DIR / "prepared_physical_single_items.csv")
    trials = load_and_clean_human_trials()
    subset, summary = summarize_human_times(trials, prepared)
    write_outputs(subset, summary)


if __name__ == "__main__":
    main()
