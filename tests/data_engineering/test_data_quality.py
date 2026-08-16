"""Validação das evidências de qualidade geradas pelo pipeline."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "deliverables" / "02_TRATAMENTO_DE_DADOS" / "data_quality_report.json"


class DataQualityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_all_sources_were_loaded(self):
        self.assertEqual(self.report["summary"]["tables"], 24)

    def test_no_duplicate_primary_keys(self):
        self.assertEqual(self.report["summary"]["duplicate_primary_keys"], 0)

    def test_no_foreign_key_orphans(self):
        self.assertEqual(self.report["summary"]["foreign_key_orphans"], 0)
