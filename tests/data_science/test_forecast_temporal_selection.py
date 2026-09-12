"""Garante que a seleção de produtos não utiliza o período de teste."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from retail_data_platform.data_science.demand_forecasting import forecast


class ForecastTemporalSelectionTest(unittest.TestCase):
    def test_top_products_are_selected_only_from_training_history(self):
        months = pd.date_range("2020-01-01", periods=30, freq="MS")
        rows = [
            {
                "order_date": month,
                "product_id": 1,
                "product_name": "Produto histórico",
                "quantity": 10,
                "refunded_qty": 0,
            }
            for month in months
        ]
        rows.extend(
            {
                "order_date": month,
                "product_id": 2,
                "product_name": "Produto visto apenas no teste",
                "quantity": 1000,
                "refunded_qty": 0,
            }
            for month in months[-6:]
        )

        with TemporaryDirectory() as temporary:
            output = Path(temporary)
            result = forecast(
                pd.DataFrame(rows), output, output / "model",
                top_n=1, horizon=1, test_months=6, seed=42,
            )

        self.assertEqual(set(result["future"].product_id), {1})
