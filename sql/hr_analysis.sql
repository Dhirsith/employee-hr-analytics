-- Definitions use one row per fictional employee. Attrition means source label Yes.
-- Currency is unspecified; income is kept in source units.

-- Overall KPI definitions
SELECT COUNT(*) AS employee_records,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS observed_attrition_rate,
       COUNT(*) FILTER (WHERE NOT attrition) AS not_labelled_attrited_count,
       AVG(age) AS mean_age, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY age) AS median_age,
       AVG(years_at_company) AS mean_years_at_company,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY years_at_company) AS median_years_at_company,
       AVG(monthly_income) AS mean_monthly_income_source_units,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monthly_income) AS median_monthly_income_source_units,
       AVG(over_time::int::numeric) AS overtime_share,
       AVG(job_satisfaction) AS mean_job_satisfaction_1_to_4
FROM public.employee_analytics;

-- Grouped rates retain denominators; do not infer causation from these differences.
SELECT department, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS attrition_rate,
       AVG(monthly_income) AS mean_monthly_income_source_units,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monthly_income) AS median_monthly_income_source_units
FROM public.employee_analytics GROUP BY department ORDER BY attrition_rate DESC;

SELECT job_role, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS attrition_rate
FROM public.employee_analytics GROUP BY job_role
ORDER BY attrition_rate DESC;

SELECT tenure_group, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS attrition_rate,
       AVG(years_at_company) AS mean_tenure
FROM public.employee_analytics GROUP BY tenure_group ORDER BY tenure_group;

SELECT age_group, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS attrition_rate
FROM public.employee_analytics GROUP BY age_group ORDER BY age_group;

SELECT job_satisfaction, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS attrition_rate
FROM public.employee_analytics GROUP BY job_satisfaction ORDER BY job_satisfaction;

SELECT work_life_balance, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS attrition_rate
FROM public.employee_analytics GROUP BY work_life_balance ORDER BY work_life_balance;

SELECT income_band, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS attrition_rate,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monthly_income) AS median_income_source_units
FROM public.employee_analytics GROUP BY income_band ORDER BY MIN(monthly_income);

SELECT over_time, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition) AS attrition_count,
       AVG(attrition::int::numeric) AS attrition_rate
FROM public.employee_analytics GROUP BY over_time ORDER BY over_time;

-- Ranking suppresses only small groups from this focused output; base detail is retained.
SELECT job_role, COUNT(*) AS employee_count,
       AVG(attrition::int::numeric) AS attrition_rate
FROM public.employee_analytics GROUP BY job_role
HAVING COUNT(*) >= 20 ORDER BY attrition_rate DESC;

SELECT department, job_role, COUNT(*) AS employee_count,
       AVG(monthly_income) AS mean_monthly_income_source_units,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monthly_income) AS median_monthly_income_source_units
FROM public.employee_analytics GROUP BY department, job_role
ORDER BY department, mean_monthly_income_source_units DESC;

-- Workforce composition: role mix as a share of its department's sample records.
WITH department_roles AS (
    SELECT department, job_role, COUNT(*) AS employee_count
    FROM public.employee_analytics GROUP BY department, job_role
)
SELECT department, job_role, employee_count,
       employee_count::numeric / SUM(employee_count) OVER (PARTITION BY department) AS department_share
FROM department_roles ORDER BY department, department_share DESC;

-- Median income by job level; sample units have no documented currency.
SELECT job_level, COUNT(*) AS employee_count,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monthly_income) AS median_income_source_units
FROM public.employee_analytics GROUP BY job_level ORDER BY job_level;

-- CASE creates transparent rate bands for a concise descriptive summary.
WITH department_rates AS (
    SELECT department, COUNT(*) AS employee_count,
           AVG(attrition::int::numeric) AS attrition_rate
    FROM public.employee_analytics GROUP BY department
)
SELECT department, employee_count, attrition_rate,
       CASE WHEN attrition_rate >= 0.20 THEN '20% or higher'
            WHEN attrition_rate >= 0.15 THEN '15% to under 20%'
            ELSE 'under 15%' END AS descriptive_rate_band
FROM department_rates ORDER BY attrition_rate DESC;

-- Rank employees by income within department and job level.
SELECT department, job_level, employee_id, monthly_income,
       RANK() OVER (PARTITION BY department, job_level ORDER BY monthly_income DESC) AS income_rank
FROM public.employee_analytics;
