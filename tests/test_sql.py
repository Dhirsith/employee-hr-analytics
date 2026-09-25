from pathlib import Path

import pandas as pd
import sqlglot

ROOT = Path(__file__).resolve().parents[1]


def test_all_sql_statements_parse_as_postgres():
    for path in (ROOT / "sql").glob("*.sql"):
        statements = sqlglot.parse(path.read_text(), read="postgres")
        assert statements
        assert all(statement is not None for statement in statements)


def test_schema_column_order_matches_processed_csv():
    from src.data_cleaning import clean_data

    raw = pd.read_csv(ROOT / "data/raw/ibm_hr_employee_attrition.csv")
    cleaned, _ = clean_data(raw)
    expected = list(cleaned.columns)
    schema = (ROOT / "sql/schema.sql").read_text()
    # The COPY command reads CSV fields by position, so enforce the table's declared order.
    create = next(s for s in sqlglot.parse(schema, read="postgres") if s.key == "create")
    actual = [column.name for column in create.this.expressions if column.key == "column" or column.__class__.__name__ == "ColumnDef"]
    assert actual == expected
