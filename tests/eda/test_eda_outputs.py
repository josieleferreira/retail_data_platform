"""Contratos dos resultados públicos de EDA e analytics."""

import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / "deliverables"


class EdaOutputTest(unittest.TestCase):
    def test_six_delivery_fronts_exist(self):
        expected = {
            "01_EDA", "02_TRATAMENTO_DE_DADOS", "03_ANALISE_DE_VENDAS",
            "04_ANALISE_DE_CLIENTES", "05_PREVISAO_DE_DEMANDAS",
            "06_SISTEMAS_DE_RECOMENDACOES",
        }
        actual = {path.name for path in DELIVERY.iterdir() if path.is_dir()}
        self.assertTrue(expected.issubset(actual))

    def test_eda_inventory_covers_all_sources(self):
        inventory = pd.read_csv(DELIVERY / "01_EDA" / "tables" / "table_inventory.csv")
        self.assertEqual(len(inventory), 24)
        self.assertGreater(inventory.rows.sum(), 0)

    def test_project_summary_and_dashboard_exist(self):
        summary = (DELIVERY / "PROJECT_SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn("Síntese técnica", summary)
        self.assertTrue((DELIVERY / "DASHBOARD_EXECUTIVO.html").exists())

    def test_raw_sources_are_not_distributed(self):
        data_dir = ROOT / "data"
        directories = {path.name for path in data_dir.iterdir() if path.is_dir()}
        files = [path for path in data_dir.iterdir() if path.is_file()]
        self.assertEqual(directories, {"raw"})
        self.assertEqual(files, [])
        self.assertEqual(len(list((data_dir / "raw").glob("*.csv"))), 0)

    def test_each_front_documents_its_sources(self):
        for folder in [path for path in DELIVERY.iterdir() if path.is_dir()]:
            source_document = folder / "DATA_SOURCES.md"
            self.assertTrue(source_document.exists())
            text = source_document.read_text(encoding="utf-8")
            for relative in text.split("`")[1::2]:
                if relative.startswith("../../data/raw/"):
                    self.assertTrue(relative.endswith(".csv"))
