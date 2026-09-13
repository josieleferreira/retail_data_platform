"""Execução do dbt sobre DuckDB temporário e retorno dos marts em memória."""

from __future__ import annotations

from pathlib import Path
import os
import re
import shutil
import subprocess

import duckdb
import pandas as pd


MART_NAMES = [
    "mart_sales_items",
    "mart_customer_360",
    "mart_product_performance",
    "mart_daily_sales",
]
SAFE_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


class DbtBuildError(RuntimeError):
    """Indica falha de modelo ou teste durante o dbt build."""


def load_raw_tables(tables: dict[str, pd.DataFrame], database_path: Path) -> None:
    """Carrega DataFrames curados no schema raw de um DuckDB descartável."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database_path)) as connection:
        connection.execute("create schema if not exists raw")
        for name, frame in sorted(tables.items()):
            if not SAFE_IDENTIFIER.fullmatch(name):
                raise ValueError(f"Nome de tabela inválido: {name}")
            connection.register("incoming_frame", frame)
            connection.execute(
                f'create or replace table raw."{name}" as select * from incoming_frame'
            )
            connection.unregister("incoming_frame")


def _invoke_dbt(arguments: list[str], command_name: str, environment: dict[str, str]) -> None:
    executable = shutil.which("dbt")
    if executable is None:
        raise DbtBuildError("Executável dbt não encontrado; instale requirements.txt")
    completed = subprocess.run([executable, *arguments], env=environment, check=False)
    if completed.returncode != 0:
        raise DbtBuildError(f"{command_name} falhou (exit code {completed.returncode})")


def build_marts_with_dbt(
    tables: dict[str, pd.DataFrame],
    project_dir: Path,
    runtime_dir: Path,
    artifact_dir: Path,
    generate_docs: bool = True,
) -> dict[str, pd.DataFrame]:
    """Executa modelos/testes dbt e devolve quatro marts como DataFrames."""
    database_path = runtime_dir / "retail_runtime.duckdb"
    target_path = artifact_dir / "target"
    log_path = artifact_dir / "logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    load_raw_tables(tables, database_path)

    environment = os.environ.copy()
    environment.update({
        "DBT_DUCKDB_PATH": database_path.resolve().as_posix(),
        "DBT_TARGET_PATH": target_path.resolve().as_posix(),
        "DBT_LOG_PATH": log_path.resolve().as_posix(),
    })
    common = [
        "--project-dir", str(project_dir.resolve()),
        "--profiles-dir", str(project_dir.resolve()),
        "--target-path", str(target_path.resolve()),
    ]
    _invoke_dbt(["build", *common], "dbt build", environment)
    build_results = target_path / "run_results.json"
    if build_results.exists():
        shutil.copy2(build_results, target_path / "run_results.build.json")
    if generate_docs:
        _invoke_dbt(["docs", "generate", *common], "dbt docs generate", environment)

    with duckdb.connect(str(database_path), read_only=True) as connection:
        return {
            name: connection.execute(f'select * from marts."{name}"').fetchdf()
            for name in MART_NAMES
        }
