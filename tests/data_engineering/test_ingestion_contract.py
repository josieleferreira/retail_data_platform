"""Testes sintéticos do contrato e da leitura das fontes."""

import csv
import sys
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from retail_data_platform.data_engineering.ingestion import (
    REQUIRED_COLUMNS,
    SourceContractError,
    extract_source,
    validate_source_contract,
)
from retail_data_platform.data_engineering.transformation import read_and_clean


def write_contract_sources(directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    for table, columns in REQUIRED_COLUMNS.items():
        with (directory / f"{table}.csv").open("w", encoding="utf-8", newline="") as stream:
            csv.writer(stream).writerow(sorted(columns))
    return sorted(directory.glob("*.csv"))


class IngestionContractTest(unittest.TestCase):
    def test_valid_contract_is_accepted_and_copied(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            raw = root / "raw"
            write_contract_sources(source)

            files = extract_source(source, raw)

            self.assertEqual(len(files), 24)
            self.assertEqual({path.stem for path in files}, set(REQUIRED_COLUMNS))

    def test_missing_table_has_clear_error(self):
        with TemporaryDirectory() as temporary:
            source = Path(temporary)
            files = write_contract_sources(source)
            (source / "customers.csv").unlink()

            with self.assertRaisesRegex(SourceContractError, "fontes ausentes: customers"):
                validate_source_contract([path for path in files if path.exists()])

    def test_missing_required_column_has_clear_error(self):
        with TemporaryDirectory() as temporary:
            source = Path(temporary)
            files = write_contract_sources(source)
            orders = source / "orders.csv"
            columns = sorted(REQUIRED_COLUMNS["orders"] - {"total"})
            with orders.open("w", encoding="utf-8", newline="") as stream:
                csv.writer(stream).writerow(columns)

            with self.assertRaisesRegex(SourceContractError, "orders.csv sem colunas obrigatórias: total"):
                validate_source_contract(files)

    def test_zip_path_traversal_is_rejected(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("../outside.csv", "id\n1\n")

            with self.assertRaisesRegex(ValueError, "caminhos inseguros"):
                extract_source(archive, root / "raw")

    def test_type_normalization_uses_expected_dtypes(self):
        with TemporaryDirectory() as temporary:
            sample = Path(temporary) / "sample.csv"
            with sample.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["id", "placed_at", "is_active", "total", "name"])
                writer.writerow([" 7 ", "2026-01-02 10:30:00", "TRUE", "19.90", " Produto "])

            frame = read_and_clean(sample)

            self.assertEqual(frame.loc[0, "id"], 7)
            self.assertEqual(frame.loc[0, "total"], 19.90)
            self.assertEqual(frame.loc[0, "name"], "Produto")
            self.assertEqual(frame.loc[0, "placed_at"], pd.Timestamp("2026-01-02 10:30:00"))
            self.assertTrue(frame.loc[0, "is_active"])
