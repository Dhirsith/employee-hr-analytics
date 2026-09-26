# Power BI dashboard specification

The repository produces Power BI-ready CSV extracts; it does not contain a `.pbix` file.

## Suggested one-page view

- KPI cards: employee records, attrition count, observed attrition rate, mean tenure, median monthly income (source units), overtime share.
- Department and job-role charts: observed attrition rate with employee count available in tooltips.
- Composition charts: department, age group, tenure group, and overtime.
- Slicers: department, job role, gender, age group, tenure group, overtime, business travel.

## Measures

Use `kpis.csv` for the fixed, overall metrics. Those precomputed rows do not recalculate when employee-level slicers change. For interactive slices, import `employee_analytics.csv` as `employee_analytics` and explicitly set `attrition` to the True/False data type in Power Query; the Python export writes boolean values, not numeric 0/1 values.

Create these measures against the employee table:

```dax
Employee Records = COUNTROWS(employee_analytics)

Attrition Count =
    COALESCE(
        CALCULATE(
            COUNTROWS(employee_analytics),
            KEEPFILTERS(employee_analytics[attrition] = TRUE())
        ),
        0
    )

Observed Attrition Rate = DIVIDE([Attrition Count], [Employee Records])
```

The count respects the current slicer context and counts records labelled True. Format the rate as a percentage and keep the denominator visible. Before publishing a dashboard, validate the unfiltered cards against the generated KPI export and verify department and job-role slices against their group tables. These are specification examples; they have not been executed in a `.pbix` report.

See Microsoft's [CALCULATE reference](https://learn.microsoft.com/dax/calculate-function-dax) for filter-context behavior. Label values as sample records and income as source units. No causality or prediction claims are supported.

## Inputs

The pipeline exports `employee_analytics.csv`, `kpis.csv`, and selected group metrics to `outputs/powerbi/`. The employee-level export omits the source row identifier. Power BI relationships/visuals remain to be authored and validated by a human; no dashboard result is claimed.

