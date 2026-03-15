# data access notes

## benchmark source

Public repo: https://github.com/Kinds-of-Intelligence-CFI/VIGNET

Relevant public files:
- `README.md`
- `access_INTUIT.txt`
- `project_files.zip`
- `build_dataset.py`
- `preprocessing_and_plotting.ipynb`

The repo README states that `project_files.zip` contains the INTUIT dataframes and that the password is in `access_INTUIT.txt`.

`access_INTUIT.txt` contains the password:
- `vignette2025`

## human results source

Published results archive: https://osf.io/phscu/

The OSF GUID `phscu` resolves to the public file `INTUIT_paper_results.zip` on node `9wyg2`.

Direct download URL:
- `https://osf.io/download/phscu/`

## exact files used

From `project_files.zip`:
- `project_files/dataframes/batteries/battery_for_humans_single.csv`
- `project_files/dataframes/dataframes/condition_single.csv`
- `project_files/dataframes/dataframes/inference_level_single.csv`
- `project_files/dataframes/INTUIT/*/*_qa_template.json`
- `project_files/dataframes/dataframes/item_df.csv`
- `project_files/dataframes/dataframes/activity_df.csv`
- `project_files/dataframes/dataframes/demand_df.csv`

From `INTUIT_paper_results.zip`:
- `paper_results/human_data_single_clean.csv`
- published AI result files used only for source inspection, not for the new benchmark contribution

## download steps

1. Run `python -m src.download_data`.
2. The script downloads `project_files.zip` from the VIGNET repo into `data/raw/project_files.zip`.
3. The script downloads `INTUIT_paper_results.zip` from OSF into `data/raw/INTUIT_paper_results.zip`.
4. The script extracts both archives with `bsdtar`.
5. Both archives use the public password `vignette2025`.

## transformation steps

1. Run `python -m src.prepare_intuit`.
2. The script loads the single-capability human battery, the condition grid, the inference-level grid, and all INTUIT QA templates.
3. Template ids are normalized to two-digit prefixes such as `01.1.0.0.a`.
4. Templates are filtered to `capability_type == "single"` and to templates whose required metadata components are all physical.
5. The resulting physical-only single-capability templates are expanded across the six human counterbalance columns `C1` to `C6`.

## human timing steps

1. Run `python -m src.extract_human_times`.
2. The script loads `human_data_single_clean.csv`.
3. It keeps Gorilla rows with `Display == "Trial"` and `Screen == "vignette"`.
4. Participants are excluded if they fail the attention check or if their median reaction time falls below 20 seconds, matching the public notebook logic.
5. Trials below 5 seconds are excluded from timing and accuracy summaries.
6. Item-level medians are computed for all valid attempts and for correct valid attempts only.

## caveats

The human data archive is public, but the OSF landing page does not enumerate the contained filenames directly. The exact filenames come from the published notebook and from inspection of the downloaded archive.
