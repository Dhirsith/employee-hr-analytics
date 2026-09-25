"""Fetch the pinned Kaggle dataset archive and verify its published checksum."""
from __future__ import annotations

import hashlib
import urllib.request
import zipfile
from pathlib import Path

URL = "https://www.kaggle.com/api/v1/datasets/download/pavansubhasht/ibm-hr-analytics-attrition-dataset?datasetVersionNumber=1"
ARCHIVE_SHA256 = "8368f123ae1ae9e30c2f19f28e766a28d7481d1486ff9aabc9e0533fefcf6be3"
RAW_DIR = Path(__file__).resolve().parents[1] / "data/raw"
ARCHIVE = RAW_DIR / "ibm-hr-analytics-attrition-dataset.zip"
SOURCE_NAME = "WA_Fn-UseC_-HR-Employee-Attrition.csv"
TARGET = RAW_DIR / "ibm_hr_employee_attrition.csv"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        request = urllib.request.Request(URL, headers={"User-Agent": "employee-hr-analytics/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response, ARCHIVE.open("wb") as output:
            output.write(response.read())
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        ARCHIVE.unlink(missing_ok=True)
        raise RuntimeError(f"Unexpected archive SHA-256: {digest}")
    with zipfile.ZipFile(ARCHIVE) as archive:
        member = next((name for name in archive.namelist() if Path(name).name == SOURCE_NAME), None)
        if member is None:
            raise RuntimeError(f"Pinned source CSV {SOURCE_NAME} not found in archive")
        TARGET.write_bytes(archive.read(member))
    print(f"Verified archive SHA-256 {digest}; extracted {TARGET}")


if __name__ == "__main__":
    main()
