# Data dictionary

The processed table has one row per source employee record. Names are snake_case; `employee_id` is the retained source `EmployeeNumber`. All source fields other than the three verified constants are retained, alongside three deterministic grouping fields.

| Field | Meaning |
|---|---|
| `attrition` | Source Yes/No outcome converted to boolean; descriptive sample label |
| `over_time` | Source Yes/No overtime field converted to boolean |
| `age_group` | 18–29, 30–39, 40–49, or 50–60 years |
| `tenure_group` | 0–2, 3–5, 6–10, 11–20, or 21+ years at company |
| `income_band` | Fixed bins of source monthly-income values: under 3,000; 3,000–4,999; 5,000–7,999; 8,000–11,999; 12,000+ |
| `monthly_income` | Source numeric amount; currency unspecified |
| `education`, `job_satisfaction`, `environment_satisfaction`, `job_involvement`, `relationship_satisfaction`, `work_life_balance` | Source ordinal scores; see original source documentation for coding |

Other source attributes are retained under snake_case names. The data is fictional and does not include event dates.
