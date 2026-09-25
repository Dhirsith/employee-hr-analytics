"""Explicit, reproducible cleaning for the IBM synthetic HR sample."""

from __future__ import annotations

import re

import pandas as pd

from src.validation import audit_source, validate_clean_data

DROP_CONSTANT_COLUMNS = ["EmployeeCount", "Over18", "StandardHours"]


def standardize_column_name(name: str) -> str:
    """Convert IBM's CamelCase source fields to stable snake_case names."""
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Audit first, then standardize, drop audited constants, and validate."""
    audit = audit_source(raw)
    invalid_category_counts = {
        key: values for key, values in audit["unexpected_categories"].items() if values
    }
    invalid_ranges = {
        key: detail for key, detail in audit["range_checks"].items() if detail["invalid_rows"]
    }
    invalid_consistency = {
        key: value for key, value in audit["tenure_consistency_violations"].items() if value
    }
    if audit["duplicate_rows"] or audit["duplicate_employee_ids"]:
        raise ValueError("Source audit found duplicate rows or employee IDs; review before cleaning.")
    if any(audit["missing_values_by_column"].values()):
        raise ValueError("Source audit found missing values; review before cleaning.")
    if invalid_category_counts or invalid_ranges or invalid_consistency:
        raise ValueError(
            "Source audit found category, range, or tenure inconsistencies; review before cleaning. "
            f"categories={invalid_category_counts}, ranges={invalid_ranges}, consistency={invalid_consistency}"
        )

    cleaned = raw.copy()
    constants = audit["constant_columns"]
    if not set(DROP_CONSTANT_COLUMNS).issubset(constants):
        raise ValueError("Expected constant fields were not constant; review the source before dropping them.")
    cleaned = cleaned.drop(columns=DROP_CONSTANT_COLUMNS)
    cleaned = cleaned.rename(columns={column: standardize_column_name(column) for column in cleaned.columns})
    cleaned = cleaned.rename(columns={"employee_number": "employee_id"})
    for column in ["attrition", "over_time"]:
        cleaned[column] = cleaned[column].map({"Yes": True, "No": False}).astype("bool")

    cleaned["age_group"] = pd.cut(
        cleaned["age"], bins=[17, 29, 39, 49, 60],
        labels=["18-29", "30-39", "40-49", "50-60"], include_lowest=True,
    )
    cleaned["tenure_group"] = pd.cut(
        cleaned["years_at_company"], bins=[-1, 2, 5, 10, 20, float("inf")],
        labels=["0-2", "3-5", "6-10", "11-20", "21+"], include_lowest=True,
    )
    cleaned["income_band"] = pd.cut(
        cleaned["monthly_income"], bins=[-1, 2999, 4999, 7999, 11999, float("inf")],
        labels=["Under 3,000", "3,000-4,999", "5,000-7,999", "8,000-11,999", "12,000+"],
        include_lowest=True,
    )
    validate_clean_data(cleaned)
    summary = {
        "source_rows": int(len(raw)),
        "source_columns": int(len(raw.columns)),
        "clean_rows": int(len(cleaned)),
        "clean_columns": int(len(cleaned.columns)),
        "rows_removed": int(len(raw) - len(cleaned)),
        "fields_dropped": DROP_CONSTANT_COLUMNS,
        "fields_retained_as_identifiers": ["EmployeeNumber -> employee_id"],
        "yes_no_fields_converted_to_boolean": ["Attrition -> attrition", "OverTime -> over_time"],
        "group_definitions": {
            "age_group": "18-29, 30-39, 40-49, 50-60 years; observed dataset range is 18-60",
            "tenure_group": "0-2, 3-5, 6-10, 11-20, 21+ years at company",
            "income_band": "fixed source-unit bands: <3,000; 3,000-4,999; 5,000-7,999; 8,000-11,999; 12,000+",
        },
    }
    return cleaned, summary
