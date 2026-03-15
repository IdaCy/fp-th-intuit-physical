from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
RESULTS_DIR = REPO_ROOT / "results"
REPORTS_DIR = REPO_ROOT / "reports"
CONFIGS_DIR = REPO_ROOT / "configs"


def ensure_dirs() -> None:
    for path in [
        DATA_DIR,
        RAW_DIR,
        INTERIM_DIR,
        RESULTS_DIR,
        RESULTS_DIR / "tables",
        RESULTS_DIR / "figures",
        RESULTS_DIR / "model_outputs",
        RESULTS_DIR / "model_outputs" / "raw",
        REPORTS_DIR,
        CONFIGS_DIR,
        REPO_ROOT / "scripts",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
