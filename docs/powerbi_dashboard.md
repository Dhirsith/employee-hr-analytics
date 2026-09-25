# Power BI dashboard specification

The repository produces Power BI-ready CSV extracts; it does not contain a `.pbix` file.

## Suggested one-page view

- KPI cards: employee records, attrition count, observed attrition rate, mean tenure, median monthly income (source units), overtime share.
- Department and job-role charts: observed attrition rate with employee count available in tooltips.
- Composition charts: department, age group, tenure group, and overtime.
- Slicers: department, job role, gender, age group, tenure group, overtime, business travel.

## Measures

Use `kpis.csv` for the already defined overall metrics. For interactive slices, calculate `Attrition Count = SUM(employee_analytics[attrition])` and `Observed Attrition Rate = DIVIDE([Attrition Count], COUNTROWS(employee_analytics))`. Keep the denominator visible. Label values as sample records and income as source units. No causality or prediction claims are supported.

## Inputs

The pipeline exports `employee_analytics.csv`, `kpis.csv`, and selected group metrics to `outputs/powerbi/`. The employee-level export omits the source row identifier. Power BI relationships/visuals remain to be authored and validated by a human; no dashboard result is claimed.
