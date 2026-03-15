from __future__ import annotations

import shutil
import subprocess
import urllib.request
from pathlib import Path

from src.utils import RAW_DIR, ensure_dirs


VIGNET_REPO_URL = "https://raw.githubusercontent.com/Kinds-of-Intelligence-CFI/VIGNET/main/project_files.zip"
OSF_RESULTS_URL = "https://osf.io/download/phscu/"
PROJECT_FILES_PASSWORD = "vignette2025"


def download_file(url: str, destination: Path) -> None:
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        destination.write_bytes(response.read())


def extract_zip(archive_path: Path, output_dir: Path, password: str | None = None) -> None:
    marker = output_dir / ".complete"
    if marker.exists():
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    command = ["bsdtar", "-xf", str(archive_path), "-C", str(output_dir)]
    if password:
        command.extend(["--passphrase", password])
    subprocess.run(command, check=True)
    marker.write_text("ok\n")


def main() -> None:
    ensure_dirs()
    if shutil.which("bsdtar") is None:
        raise RuntimeError("bsdtar is required to extract the published INTUIT archives")

    vignet_zip = RAW_DIR / "project_files.zip"
    osf_zip = RAW_DIR / "INTUIT_paper_results.zip"

    download_file(VIGNET_REPO_URL, vignet_zip)
    download_file(OSF_RESULTS_URL, osf_zip)

    extract_zip(vignet_zip, RAW_DIR / "vignet_repo", password=PROJECT_FILES_PASSWORD)
    extract_zip(osf_zip, RAW_DIR / "osf_results", password=PROJECT_FILES_PASSWORD)


if __name__ == "__main__":
    main()
