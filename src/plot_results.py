from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.utils import RESULTS_DIR, ensure_dirs


def main() -> None:
    ensure_dirs()
    sns.set_theme(style="whitegrid")

    item_level = pd.read_csv(RESULTS_DIR / "tables" / "item_level_results.csv")
    by_time = pd.read_csv(RESULTS_DIR / "tables" / "accuracy_by_time_bin.csv")

    plt.figure(figsize=(8, 5))
    sns.histplot(item_level[["item_instance_id", "human_median_seconds_all_valid"]].drop_duplicates(), x="human_median_seconds_all_valid", bins=12)
    plt.xlabel("Median human time per item instance (s)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "figures" / "human_time_histogram.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.barplot(data=by_time, x="time_bin", y="accuracy", hue="model")
    plt.xlabel("Human time bin")
    plt.ylabel("Model accuracy")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "figures" / "accuracy_by_time_bin.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.lineplot(data=by_time, x="median_human_seconds", y="accuracy", hue="model", marker="o")
    plt.xlabel("Median human time within bin (s)")
    plt.ylabel("Model accuracy")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "figures" / "accuracy_vs_human_time.png", dpi=200)
    plt.close()


if __name__ == "__main__":
    main()
