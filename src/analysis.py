"""Descriptive workforce metrics with explicit sample denominators."""

from __future__ import annotations

import pandas as pd

MIN_GROUP_SIZE = 20


def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Return single-row overall metrics; rates describe this dataset only."""
    n = len(df)
    attrited = int(df["attrition"].sum())
    return pd.DataFrame([{
        "employee_records": n,
        "attrition_count": attrited,
        "observed_attrition_rate": attrited / n if n else 0.0,
        "not_labelled_attrited_count": n - attrited,
        "mean_age": df["age"].mean(),
        "median_age": df["age"].median(),
        "mean_years_at_company": df["years_at_company"].mean(),
        "median_years_at_company": df["years_at_company"].median(),
        "mean_monthly_income_source_units": df["monthly_income"].mean(),
        "median_monthly_income_source_units": df["monthly_income"].median(),
        "overtime_count": int(df["over_time"].sum()),
        "overtime_share": df["over_time"].mean(),
        "mean_job_satisfaction_1_to_4": df["job_satisfaction"].mean(),
    }])


def group_metrics(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Group employee count and attrition rate, retaining denominator and flags."""
    result = (df.groupby(dimension, observed=False, dropna=False)
              .agg(employee_count=("employee_id", "size"),
                   attrition_count=("attrition", "sum"),
                   mean_monthly_income=("monthly_income", "mean"),
                   median_monthly_income=("monthly_income", "median"))
              .reset_index())
    result["attrition_rate"] = result["attrition_count"] / result["employee_count"]
    result["small_group"] = result["employee_count"] < MIN_GROUP_SIZE
    return result


def all_group_metrics(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    dimensions = ["department", "job_role", "age_group", "tenure_group", "over_time",
                  "job_satisfaction", "business_travel", "marital_status", "education_field",
                  "job_level", "income_band"]
    return {column: group_metrics(df, column) for column in dimensions}


def build_findings(kpis: pd.DataFrame, groups: dict[str, pd.DataFrame]) -> str:
    k = kpis.iloc[0]
    role = groups["job_role"].query("employee_count >= @MIN_GROUP_SIZE").sort_values("attrition_rate", ascending=False)
    dept = groups["department"].sort_values("attrition_rate", ascending=False)
    return "\n".join([
        "# Verified descriptive findings", "",
        "These findings describe only the fictional, static sample. Rates are not predictions or causal estimates.", "",
        f"- The validated sample contains **{int(k.employee_records):,} employee records**; **{int(k.attrition_count):,}** carry the attrition label Yes (**{k.observed_attrition_rate:.1%}** of records).",
        f"- Mean age is **{k.mean_age:.1f} years** (median {k.median_age:.0f}); mean company tenure is **{k.mean_years_at_company:.1f} years** (median {k.median_years_at_company:.0f}).",
        f"- Overtime is labelled Yes for **{int(k.overtime_count):,} records** ({k.overtime_share:.1%}).",
        f"- Department rates in this sample range from **{dept.attrition_rate.min():.1%} to {dept.attrition_rate.max():.1%}**; group sizes are shown in the related table.",
        f"- Among job roles with at least {MIN_GROUP_SIZE} records, the highest observed rate is **{role.iloc[0].attrition_rate:.1%}** for {role.iloc[0].job_role} (n={int(role.iloc[0].employee_count)}). This is descriptive and should not be interpreted as a risk score.",
        "",
        "Income values are reported in source units because currency is unspecified. Small groups are retained in tables and marked; ranked summaries use the stated minimum group size.",
    ]) + "\n"
