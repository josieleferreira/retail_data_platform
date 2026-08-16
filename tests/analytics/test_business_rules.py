"""Reconciliação dos marts em memória e regras comerciais."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from retail_data_platform.data_engineering.transformation import curate
from retail_data_platform.data_engineering.warehouse import build_marts_in_memory


class BusinessRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_files = sorted((ROOT / "data" / "raw").glob("*.csv"))
        if len(source_files) != 24:
            raise unittest.SkipTest("As fontes completas não são distribuídas no repositório público.")
        cls.tables = curate(source_files)
        cls.marts = build_marts_in_memory(cls.tables, ROOT / "sql")

    def test_sales_only_paid_orders(self):
        paid_ids = set(self.tables["orders"].loc[self.tables["orders"].status == "paid", "id"])
        self.assertTrue(set(self.marts["mart_sales_items"].order_id).issubset(paid_ids))

    def test_no_negative_effective_quantity(self):
        sales = self.marts["mart_sales_items"]
        self.assertEqual(int(((sales.quantity - sales.refunded_qty) < 0).sum()), 0)

    def test_financial_identity_orders(self):
        orders = self.tables["orders"]
        mismatches = ((orders.subtotal - orders.discount_amount - orders.total).abs() > 0.011).sum()
        self.assertEqual(int(mismatches), 0)

    def test_revenue_reconciles(self):
        mart_total = round(self.marts["mart_sales_items"].net_revenue.sum(), 2)
        paid_total = round(self.tables["orders"].loc[self.tables["orders"].status == "paid", "total"].sum(), 2)
        refund_total = round(self.tables["returns"].loc[self.tables["returns"].status == "completed", "total_refund_amount"].sum(), 2)
        self.assertLess(abs(mart_total - (paid_total - refund_total)), 0.05)
