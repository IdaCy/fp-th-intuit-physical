from __future__ import annotations

import pandas as pd

from src.utils import INTERIM_DIR, RAW_DIR, RESULTS_DIR, ensure_dirs, load_template_metadata, normalize_template_id, parse_vignette_options


def melt_grid(path: str, value_name: str) -> pd.DataFrame:
    grid = pd.read_csv(path)
    grid["id"] = grid["id"].map(normalize_template_id)
    melted = grid.melt(id_vars=["id"], var_name="counterbalance", value_name=value_name)
    melted["counterbalance"] = melted["counterbalance"].astype(int)
    return melted


def build_prepared_dataset() -> pd.DataFrame:
    battery_path = RAW_DIR / "vignet_repo" / "project_files" / "dataframes" / "batteries" / "battery_for_humans_single.csv"
    battery = pd.read_csv(battery_path)
    battery = battery[battery["display"] == "Trial"].copy()
    battery["template_id"] = battery["id"].map(normalize_template_id)

    template_metadata = load_template_metadata()
    battery = battery.merge(template_metadata, on="template_id", how="left")
    battery = battery[(battery["capability_type"] == "single") & (battery["is_physical_only"] == 1)].copy()

    condition_grid = melt_grid(
        RAW_DIR / "vignet_repo" / "project_files" / "dataframes" / "dataframes" / "condition_single.csv",
        "condition",
    )
    inference_grid = melt_grid(
        RAW_DIR / "vignet_repo" / "project_files" / "dataframes" / "dataframes" / "inference_level_single.csv",
        "inference_level",
    )

    records: list[dict[str, object]] = []
    for _, row in battery.iterrows():
        for counterbalance in range(1, 7):
            vignette = row[f"C{counterbalance}"]
            correct_answer = int(float(row[f"A{counterbalance}"]))
            option_map = parse_vignette_options(vignette)
            records.append(
                {
                    "item_instance_id": f"{row['template_id']}__c{counterbalance}",
                    "template_id": row["template_id"],
                    "counterbalance": counterbalance,
                    "base_context": row["base_context"],
                    "physical_subcategory": row["base_context"],
                    "required_components": row["required_components"],
                    "provided_components": row["provided_components"],
                    "novelty": row["novelty"],
                    "causal_type": row["causal_type"],
                    "causal_direction": row["causal_direction"],
                    "vignette": vignette,
                    "correct_answer_number": correct_answer,
                    **option_map,
                }
            )

    prepared = pd.DataFrame(records)
    prepared = prepared.merge(condition_grid, left_on=["template_id", "counterbalance"], right_on=["id", "counterbalance"], how="left")
    prepared = prepared.merge(
        inference_grid,
        left_on=["template_id", "counterbalance"],
        right_on=["id", "counterbalance"],
        how="left",
        suffixes=("", "_inference"),
    )
    prepared = prepared.drop(columns=["id", "id_inference"])
    prepared = prepared.sort_values(["base_context", "template_id", "counterbalance"]).reset_index(drop=True)
    return prepared


def write_outputs(prepared: pd.DataFrame) -> None:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(INTERIM_DIR / "prepared_physical_single_items.csv", index=False)

    summary = (
        prepared.groupby(["base_context", "inference_level"], as_index=False)
        .agg(item_instances=("item_instance_id", "count"), templates=("template_id", "nunique"))
        .sort_values(["base_context", "inference_level"])
    )
    summary.to_csv(RESULTS_DIR / "prepared_dataset_summary.csv", index=False)


def main() -> None:
    ensure_dirs()
    prepared = build_prepared_dataset()
    write_outputs(prepared)


if __name__ == "__main__":
    main()
