from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


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


def normalize_template_id(template_id: str) -> str:
    parts = str(template_id).split(".")
    if parts and parts[0].isdigit():
        parts[0] = parts[0].zfill(2)
    return ".".join(parts)


def parse_vignette_options(vignette: str) -> dict[str, str]:
    matches = re.findall(r"\n([1-4])\. (.+?)(?=\n[1-4]\. |\Z)", vignette.strip(), flags=re.S)
    return {f"option_{number}": text.strip() for number, text in matches}


def load_template_metadata() -> pd.DataFrame:
    root = RAW_DIR / "vignet_repo" / "project_files" / "dataframes" / "INTUIT"
    rows: list[dict[str, object]] = []
    for path in root.glob("*/*_qa_template.json"):
        data = json.loads(path.read_text())
        required = data["metadata"]["required"]
        rows.append(
            {
                "template_id": normalize_template_id(data["id"]),
                "base_context": data["base_context"],
                "capability_type": data["capability_type"],
                "required_components": "|".join(required),
                "is_physical_only": int(all(component.startswith("physical_knowledge_") for component in required)),
                "has_social_component": int(any(component.startswith("social_knowledge_") for component in required)),
                "provided_components": "|".join(data["metadata"]["provided"]),
                "novelty": data["metadata"]["novelty"],
                "causal_type": data["metadata"]["causal_type"],
                "causal_direction": data["metadata"]["causal_direction"],
            }
        )
    return pd.DataFrame(rows).drop_duplicates()
