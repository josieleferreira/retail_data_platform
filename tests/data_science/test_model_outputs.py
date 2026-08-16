"""Contratos mínimos das previsões e recomendações."""

import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


class ModelOutputTest(unittest.TestCase):
    def test_forecast_contract(self):
        path = ROOT / "deliverables" / "05_PREVISAO_DE_DEMANDAS" / "demand_forecast_3_months.csv"
        frame = pd.read_csv(path)
        self.assertEqual(set(["product_id", "product_name", "month", "prediction"]) - set(frame.columns), set())
        self.assertTrue((frame.prediction >= 0).all())
        self.assertEqual(frame.month.nunique(), 3)

    def test_recommendation_contract(self):
        path = ROOT / "deliverables" / "06_SISTEMAS_DE_RECOMENDACOES" / "product_recommendations.csv"
        frame = pd.read_csv(path)
        self.assertTrue({"source_product_id", "recommended_product_id", "confidence", "lift", "support"}.issubset(frame.columns))
        self.assertTrue((frame.source_product_id != frame.recommended_product_id).all())
