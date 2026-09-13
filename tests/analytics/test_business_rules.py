"""Reconciliação dos marts em memória e regras comerciais."""

import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from retail_data_platform.data_engineering.transformation import curate
from retail_data_platform.data_engineering.dbt_warehouse import build_marts_with_dbt


class SyntheticBusinessRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tables = {
            "orders": pd.DataFrame([{
                "id": 1, "order_number": "O-1", "placed_at": "2026-01-02",
                "customer_id": 1, "channel": "ecommerce", "location_id": 1,
                "status": "paid", "subtotal": 110.0, "discount_amount": 10.0, "total": 100.0,
            }]),
            "order_items": pd.DataFrame([{
                "id": 1, "order_id": 1, "product_variant_id": 1,
                "quantity": 2.0, "unit_price": 55.0, "line_total": 110.0,
            }]),
            "product_variants": pd.DataFrame([{"id": 1, "product_id": 1, "cost_price": 40.0}]),
            "products": pd.DataFrame([{"id": 1, "name": "Produto A", "category_id": 1, "brand_id": 1}]),
            "categories": pd.DataFrame([{"id": 1, "name": "Categoria A"}]),
            "brands": pd.DataFrame([{"id": 1, "name": "Marca A"}]),
            "customers": pd.DataFrame([{"id": 1, "legal_name": "Cliente sintético", "person_type": "PJ"}]),
            "returns": pd.DataFrame([{"id": 1, "order_id": 1, "status": "completed", "total_refund_amount": 50.0}]),
            "return_items": pd.DataFrame([{
                "id": 1, "return_id": 1, "order_item_id": 1,
                "quantity": 1.0, "action": "refund", "unit_refund_amount": 50.0,
            }]),
        }
        from tempfile import TemporaryDirectory
        cls._temporary = TemporaryDirectory()
        temporary = Path(cls._temporary.name)
        cls.dbt_artifacts = temporary / "artifacts" / "target"
        cls.marts = build_marts_with_dbt(
            tables, ROOT / "dbt", temporary / "runtime", temporary / "artifacts",
            generate_docs=False,
        )

    @classmethod
    def tearDownClass(cls):
        cls._temporary.cleanup()

    def test_discount_refund_and_cost_are_reconciled(self):
        sale = self.marts["mart_sales_items"].iloc[0]
        self.assertAlmostEqual(sale.allocated_discount, 10.0)
        self.assertAlmostEqual(sale.refund_amount, 50.0)
        self.assertAlmostEqual(sale.net_revenue, 50.0)
        self.assertAlmostEqual(sale.adjusted_cogs, 40.0)
        self.assertAlmostEqual(sale.gross_profit, 10.0)

    def test_calendar_mart_contains_the_sale_date(self):
        daily = self.marts["mart_daily_sales"]
        self.assertEqual(len(daily), 1)
        self.assertAlmostEqual(daily.iloc[0].net_revenue, 50.0)

    def test_dbt_build_artifacts_are_generated(self):
        self.assertTrue((self.dbt_artifacts / "manifest.json").exists())
        self.assertTrue((self.dbt_artifacts / "run_results.build.json").exists())


class BusinessRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_files = sorted((ROOT / "data" / "raw").glob("*.csv"))
        if len(source_files) != 24:
            raise unittest.SkipTest("As fontes completas não são distribuídas no repositório público.")
        cls.tables = curate(source_files)
        from tempfile import TemporaryDirectory
        cls._temporary = TemporaryDirectory()
        temporary = Path(cls._temporary.name)
        cls.marts = build_marts_with_dbt(
            cls.tables, ROOT / "dbt", temporary / "runtime", temporary / "artifacts",
            generate_docs=False,
        )

    @classmethod
    def tearDownClass(cls):
        cls._temporary.cleanup()

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
