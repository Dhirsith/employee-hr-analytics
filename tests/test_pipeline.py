from pathlib import Path

import pandas as pd
import pytest

from src.analysis import calculate_kpis, group_metrics
from src.data_cleaning import clean_data, standardize_column_name

DATA = Path(__file__).resolve().parents[1] / "data/raw/ibm_hr_employee_attrition.csv"


@pytest.fixture(scope="module")
def raw():
    return pd.read_csv(DATA)


def test_expected_source_quality_and_cleaning(raw):
    clean, summary = clean_data(raw)
    assert len(clean) == 1470
    assert clean.employee_id.is_unique
    assert clean.isna().sum().sum() == 0
    assert summary["rows_removed"] == 0
    assert summary["fields_dropped"] == ["EmployeeCount", "Over18", "StandardHours"]


def test_metric_denominators(raw):
    clean, _ = clean_data(raw)
    kpi = calculate_kpis(clean).iloc[0]
    assert kpi.employee_records == 1470
    assert kpi.attrition_count == 237
    assert kpi.observed_attrition_rate == pytest.approx(237 / 1470)
    assert kpi.not_labelled_attrited_count == 1233
    assert kpi.overtime_count == 416
    assert kpi.overtime_share == pytest.approx(416 / 1470)


def test_group_rate_retains_denominator_and_small_flag():
    frame = pd.DataFrame({"employee_id": range(4), "department": ["A", "A", "B", "B"],
                          "attrition": [True, False, True, True], "monthly_income": [10, 20, 30, 40]})
    grouped = group_metrics(frame, "department").set_index("department")
    assert grouped.loc["A", "employee_count"] == 2
    assert grouped.loc["A", "attrition_rate"] == pytest.approx(0.5)
    assert grouped.loc["B", "attrition_rate"] == pytest.approx(1.0)
    assert grouped.small_group.all()


def test_name_standardization():
    assert standardize_column_name("YearsWithCurrManager") == "years_with_curr_manager"


def test_age_tenure_and_income_band_boundaries(raw):
    sample = raw.head(5).copy()
    sample["Age"] = [18, 29, 30, 49, 50]
    sample["TotalWorkingYears"] = 40
    sample["YearsAtCompany"] = [0, 2, 3, 20, 21]
    sample["YearsInCurrentRole"] = [0, 1, 2, 10, 20]
    sample["YearsWithCurrManager"] = [0, 1, 2, 10, 20]
    sample["MonthlyIncome"] = [1009, 2999, 3000, 4999, 5000]
    clean, _ = clean_data(sample)
    assert clean.age_group.astype(str).tolist() == ["18-29", "18-29", "30-39", "40-49", "50-60"]
    assert clean.tenure_group.astype(str).tolist() == ["0-2", "0-2", "3-5", "11-20", "21+"]
    assert clean.income_band.astype(str).tolist() == ["Under 3,000", "Under 3,000", "3,000-4,999", "3,000-4,999", "5,000-7,999"]


def test_cleaning_fails_on_missing_values(raw):
    invalid = raw.copy()
    invalid.loc[0, "Age"] = None
    with pytest.raises(ValueError, match="missing values"):
        clean_data(invalid)


def test_cleaning_fails_on_tenure_inconsistency(raw):
    invalid = raw.copy()
    invalid.loc[0, "YearsAtCompany"] = invalid.loc[0, "TotalWorkingYears"] + 1
    with pytest.raises(ValueError, match="inconsistencies"):
        clean_data(invalid)
