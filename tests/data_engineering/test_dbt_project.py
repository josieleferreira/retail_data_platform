from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pandas as pd

from retail_data_platform.data_engineering.dbt_warehouse import load_raw_tables


ROOT = Path(__file__).resolve().parents[2]


class DbtProjectTest(unittest.TestCase):
    def test_project_has_expected_layers_and_four_marts(self):
        models = ROOT / "dbt" / "models"
        self.assertTrue((models / "staging").is_dir())
        self.assertTrue((models / "intermediate").is_dir())
        marts = sorted((models / "marts").glob("mart_*.sql"))
        self.assertEqual(len(marts), 4)

    def test_invalid_table_identifier_is_rejected_before_sql(self):
        with TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "Nome de tabela inválido"):
                load_raw_tables(
                    {"orders;drop": pd.DataFrame({"id": [1]})},
                    Path(temporary) / "runtime.duckdb",
                )
