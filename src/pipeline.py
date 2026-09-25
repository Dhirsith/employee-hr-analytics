"""Run the audit, cleaning, descriptive analysis, exports, and figures."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.analysis import all_group_metrics, build_findings, calculate_kpis
from src.data_cleaning import clean_data
from src.figures import create_figures
from src.validation import audit_source

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/ibm_hr_employee_attrition.csv"


def run_pipeline(source: Path = RAW, root: Path = ROOT) -> dict:
    raw = pd.read_csv(source)
    audit = audit_source(raw)
    cleaned, cleaning = clean_data(raw)
    (root / "data/processed").mkdir(parents=True, exist_ok=True)
    (root / "outputs/tables").mkdir(parents=True, exist_ok=True)
    (root / "outputs/powerbi").mkdir(parents=True, exist_ok=True)
    (root / "outputs/tables/source_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    (root / "outputs/tables/cleaning_summary.json").write_text(json.dumps(cleaning, indent=2) + "\n")
    cleaned.to_csv(root / "data/processed/employee_analytics.csv", index=False)
    kpis = calculate_kpis(cleaned)
    kpis.to_csv(root / "outputs/tables/kpis.csv", index=False)
    groups = all_group_metrics(cleaned)
    for dimension, table in groups.items():
        table.to_csv(root / "outputs/tables" / f"{dimension}_metrics.csv", index=False)
    (root / "outputs/tables/key_findings.md").write_text(build_findings(kpis, groups))
    kpi_long = kpis.melt(var_name="metric", value_name="value")
    kpi_long.to_csv(root / "outputs/powerbi/kpis.csv", index=False)
    for dimension in ["department", "job_role", "age_group", "tenure_group", "over_time", "job_satisfaction", "income_band"]:
        groups[dimension].to_csv(root / "outputs/powerbi" / f"{dimension}_metrics.csv", index=False)
    # Employee-level Power BI extract deliberately excludes the source row ID.
    cleaned.drop(columns=["employee_id"]).to_csv(root / "outputs/powerbi/employee_analytics.csv", index=False)
    figures = create_figures(cleaned, root / "outputs/figures")
    return {"audit": audit, "cleaning": cleaning, "kpis": kpis.iloc[0].to_dict(), "figures": figures}


if __name__ == "__main__":
    result = run_pipeline()
    print(json.dumps(result, indent=2, default=str))
