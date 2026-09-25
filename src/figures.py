"""Generate reproducible, sample-level descriptive figures."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid", palette="deep")


def create_figures(df: pd.DataFrame, output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    def save(name: str):
        plt.tight_layout()
        plt.savefig(output_dir / name, dpi=150, bbox_inches="tight")
        plt.close()
        generated.append(name)

    counts = df.groupby("department", observed=True).size().sort_values()
    counts.plot(kind="barh", color="#2563a6")
    plt.title("Employee records by department")
    plt.xlabel("Employee records")
    save("department_headcount.png")

    rates = df.groupby("department", observed=True)["attrition"].mean().sort_values()
    rates.plot(kind="barh", color="#d27842")
    plt.title("Observed attrition rate by department")
    plt.xlabel("Attrition rate")
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
    save("department_attrition.png")

    role = df.groupby("job_role", observed=True).agg(n=("employee_id", "size"), rate=("attrition", "mean"))
    role = role.sort_values("rate")
    role["rate"].plot(kind="barh", color="#d27842")
    plt.title("Observed attrition rate by job role")
    plt.xlabel("Attrition rate (counts shown in group table)")
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
    save("job_role_attrition.png")

    tenure_plot = df.assign(attrition_label=df["attrition"].map({False: "No", True: "Yes"}))
    sns.histplot(data=tenure_plot, x="years_at_company", hue="attrition_label", multiple="stack", discrete=True)
    plt.title("Years at company by source attrition label")
    plt.xlabel("Years at company")
    save("tenure_distribution.png")

    overtime_plot = df.assign(
        overtime_label=df["over_time"].map({False: "No", True: "Yes"}),
        attrition_rate=df["attrition"].astype(float),
    )
    sns.barplot(data=overtime_plot, x="overtime_label", y="attrition_rate", errorbar=None, color="#5285a5")
    plt.title("Observed attrition rate by overtime label")
    plt.xlabel("Overtime (source label)")
    plt.ylabel("Attrition rate")
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
    save("overtime_attrition.png")

    sns.barplot(data=df, x="job_satisfaction", y="attrition", errorbar=None, color="#5285a5")
    plt.title("Observed attrition rate by job satisfaction score")
    plt.xlabel("Job satisfaction (1–4 source scale)")
    plt.ylabel("Attrition rate")
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
    save("satisfaction_attrition.png")

    sns.histplot(data=df, x="monthly_income", bins=30, color="#5285a5")
    plt.title("Monthly income distribution (source units)")
    plt.xlabel("Monthly income (source units; currency unspecified)")
    save("monthly_income_distribution.png")
    return generated
