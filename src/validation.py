"""Source audit and explicit validation rules for the IBM sample."""

from __future__ import annotations

from typing import Any

import pandas as pd


EXPECTED_CATEGORIES = {
    "Attrition": {"Yes", "No"},
    "BusinessTravel": {"Non-Travel", "Travel_Rarely", "Travel_Frequently"},
    "Department": {"Human Resources", "Research & Development", "Sales"},
    "EducationField": {
        "Human Resources", "Life Sciences", "Marketing", "Medical", "Other", "Technical Degree"
    },
    "Gender": {"Female", "Male"},
    "JobRole": {
        "Healthcare Representative", "Human Resources", "Laboratory Technician", "Manager",
        "Manufacturing Director", "Research Director", "Research Scientist", "Sales Executive",
        "Sales Representative",
    },
    "MaritalStatus": {"Divorced", "Married", "Single"},
    "Over18": {"Y"},
    "OverTime": {"Yes", "No"},
}

SCORE_COLUMNS = {
    "Education": (1, 5),
    "EnvironmentSatisfaction": (1, 4),
    "JobInvolvement": (1, 4),
    "JobLevel": (1, 5),
    "JobSatisfaction": (1, 4),
    "PerformanceRating": (3, 4),
    "RelationshipSatisfaction": (1, 4),
    "StockOptionLevel": (0, 3),
    "WorkLifeBalance": (1, 4),
}

NON_NEGATIVE_COLUMNS = [
    "DailyRate", "DistanceFromHome", "EmployeeNumber", "HourlyRate", "MonthlyIncome",
    "MonthlyRate", "NumCompaniesWorked", "PercentSalaryHike", "StandardHours",
    "TotalWorkingYears", "TrainingTimesLastYear", "YearsAtCompany", "YearsInCurrentRole",
    "YearsSinceLastPromotion", "YearsWithCurrManager",
]


def audit_source(df: pd.DataFrame) -> dict[str, Any]:
    """Summarize raw data before applying cleaning rules."""
    category_issues = {}
    for column, expected in EXPECTED_CATEGORIES.items():
        if column in df:
            unexpected = sorted(set(df[column].dropna().astype(str)) - expected)
            category_issues[column] = unexpected

    ranges = {}
    for column in df.select_dtypes(include="number").columns:
        values = df[column].dropna()
        ranges[column] = {
            "minimum": float(values.min()) if not values.empty else None,
            "maximum": float(values.max()) if not values.empty else None,
            "unique_values": int(values.nunique()),
        }

    impossible = {}
    for column, (minimum, maximum) in SCORE_COLUMNS.items():
        if column in df:
            bad = int((~df[column].between(minimum, maximum) & df[column].notna()).sum())
            impossible[column] = {"allowed_min": minimum, "allowed_max": maximum, "invalid_rows": bad}
    for column in NON_NEGATIVE_COLUMNS:
        if column in df:
            impossible[column] = {
                "allowed_min": 0,
                "allowed_max": None,
                "invalid_rows": int((df[column].lt(0) & df[column].notna()).sum()),
            }

    consistency = {}
    if {"YearsAtCompany", "TotalWorkingYears"}.issubset(df.columns):
        consistency["tenure_not_overall_experience"] = int(
            (df["YearsAtCompany"] > df["TotalWorkingYears"]).sum()
        )
    if {"YearsInCurrentRole", "YearsAtCompany"}.issubset(df.columns):
        consistency["current_role_tenure_not_over_company_tenure"] = int(
            (df["YearsInCurrentRole"] > df["YearsAtCompany"]).sum()
        )
    if {"YearsWithCurrManager", "YearsAtCompany"}.issubset(df.columns):
        consistency["manager_tenure_not_over_company_tenure"] = int(
            (df["YearsWithCurrManager"] > df["YearsAtCompany"]).sum()
        )

    constants = [column for column in df if df[column].nunique(dropna=False) <= 1]
    duplicate_employee_ids = int(df["EmployeeNumber"].duplicated().sum()) if "EmployeeNumber" in df else None
    return {
        "source_rows": int(len(df)),
        "source_columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_employee_ids": duplicate_employee_ids,
        "missing_values_by_column": {k: int(v) for k, v in df.isna().sum().items()},
        "data_types": {k: str(v) for k, v in df.dtypes.items()},
        "numeric_ranges": ranges,
        "unexpected_categories": category_issues,
        "range_checks": impossible,
        "tenure_consistency_violations": consistency,
        "constant_columns": constants,
        "candidate_redundant_columns": ["EmployeeCount", "Over18", "StandardHours"],
    }


def validate_clean_data(df: pd.DataFrame) -> None:
    """Raise ValueError with all violations found in the cleaned employee table."""
    errors: list[str] = []
    if df.empty:
        errors.append("employee dataset is empty")
    if "employee_id" not in df:
        errors.append("employee_id is required")
    elif df["employee_id"].isna().any() or df["employee_id"].duplicated().any():
        errors.append("employee_id values must be present and unique")
    if df.isna().any().any():
        errors.append("cleaned dataset contains missing values")

    expected = {
        "attrition": {True, False},
        "business_travel": {"Non-Travel", "Travel_Rarely", "Travel_Frequently"},
        "department": {"Human Resources", "Research & Development", "Sales"},
        "education_field": {
            "Human Resources", "Life Sciences", "Marketing", "Medical", "Other", "Technical Degree"
        },
        "gender": {"Female", "Male"},
        "job_role": EXPECTED_CATEGORIES["JobRole"],
        "marital_status": {"Divorced", "Married", "Single"},
        "over_time": {True, False},
    }
    for column, valid in expected.items():
        if column in df:
            actual = set(df[column].dropna().unique().tolist())
            if not actual.issubset(valid):
                errors.append(f"{column} contains invalid categories: {sorted(actual - valid, key=str)}")
        else:
            errors.append(f"required column missing: {column}")

    if "age" in df and not df["age"].between(18, 60).all():
        errors.append("age must remain within the source sample range 18..60")
    for column in ["years_at_company", "total_working_years", "years_in_current_role", "years_with_curr_manager"]:
        if column in df and df[column].lt(0).any():
            errors.append(f"{column} must be non-negative")
    if "monthly_income" in df and df["monthly_income"].lt(0).any():
        errors.append("monthly_income must be non-negative")
    for column in ["environment_satisfaction", "job_involvement", "job_satisfaction", "relationship_satisfaction", "work_life_balance"]:
        if column in df and not df[column].between(1, 4).all():
            errors.append(f"{column} must be an integer score from 1 to 4")

    for child, parent in [
        ("years_at_company", "total_working_years"),
        ("years_in_current_role", "years_at_company"),
        ("years_with_curr_manager", "years_at_company"),
    ]:
        if {child, parent}.issubset(df.columns) and (df[child] > df[parent]).any():
            errors.append(f"{child} must not exceed {parent}")

    if errors:
        raise ValueError("Data validation failed:\n- " + "\n- ".join(errors))
