# Dataset files

The source CSV and generated processed data are intentionally excluded from Git. Obtain the pinned Kaggle dataset version with:

```bash
python scripts/download_data.py
```

The script downloads Kaggle dataset `pavansubhasht/ibm-hr-analytics-attrition-dataset`, version 1, validates its recorded SHA-256, and extracts `ibm_hr_employee_attrition.csv` into `data/raw/`. It does not use Kaggle credentials. Review `docs/methodology.md` and the project README before interpreting the fictional sample.
