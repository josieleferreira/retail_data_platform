"""Modelagem SQL em memória, sem persistir uma segunda cópia dos dados."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import pandas as pd


MART_NAMES = [
    "mart_sales_items",
    "mart_customer_360",
    "mart_product_performance",
    "mart_daily_sales",
]


def build_marts_in_memory(
    tables: dict[str, pd.DataFrame], sql_dir: Path
) -> dict[str, pd.DataFrame]:
    """Carrega tabelas em SQLite temporário e devolve os marts como DataFrames."""
    with sqlite3.connect(":memory:") as connection:
        for name, frame in tables.items():
            output = frame.copy()
            for column in output.select_dtypes(include=["datetime", "datetimetz"]).columns:
                output[column] = output[column].dt.strftime("%Y-%m-%d %H:%M:%S")
            output.to_sql(name, connection, index=False, if_exists="replace")
        for sql_path in sorted(sql_dir.rglob("*.sql")):
            connection.executescript(sql_path.read_text(encoding="utf-8"))
        return {
            name: pd.read_sql_query(f"SELECT * FROM {name}", connection)
            for name in MART_NAMES
        }

