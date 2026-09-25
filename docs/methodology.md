# Methodology and definitions

## Source and scope

The source is the fictional, static IBM HR Analytics sample distributed by Kaggle dataset version 1. Its 1,470 rows are employee records with one Yes/No attrition outcome label and no event dates. This supports descriptive comparisons within the sample only. It does not support time-series or causal interpretation, current headcount, prediction, or inference about any real organization.

## Audit and cleaning

The pipeline checks duplicate rows and identifiers, missing values, categories, numeric bounds, tenure relationships, and constants. It fails visibly on unexpected problems. It drops only `EmployeeCount`, `Over18`, and `StandardHours` after confirming each is constant, standardizes field names, keeps `EmployeeNumber` as `employee_id`, and converts source Yes/No fields to booleans. Age, tenure, and income bands are deterministic bins documented in the cleaning summary. No rows are imputed or removed.

## Definitions

- Attrition means the source label Yes. `False`/No is described as “not labelled attrited,” not as active employment.
- Overall attrition rate is Yes records divided by all records; group rate is Yes records divided by records in that group.
- Overtime share uses Yes records divided by all records.
- Age and company tenure use arithmetic mean and median; income uses source values without a currency assumption.
- Job satisfaction is an ordinal source score from 1 to 4. Its mean is a descriptive summary, not a validated interval scale.
- Group tables retain all categories and their denominators. Focused ranked findings require at least 20 records; this is a display rule, not a statistical significance threshold.
- The SQL and Python tables use the same row-level definitions. PostgreSQL SQL is parsed in automated checks; unless run against a live database, parsing does not verify query results.

## Reproduction

From the repository root, run `python scripts/download_data.py`, then `python -m src.pipeline`. The processed employee table is written locally to `data/processed/employee_analytics.csv`. For PostgreSQL, run `sql/schema.sql` and import the CSV, for example:

```sql
\copy public.employee_analytics FROM 'data/processed/employee_analytics.csv' WITH (FORMAT csv, HEADER true)
```

The source `employee_id` is a data identifier, not an analytical measure. The Power BI employee export omits it.
