from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from retail_data_platform.governance.quality_gates import QualityGateError, evaluate_quality_gates


def _report(duplicates=0, orphans=0, order_mismatches=0, item_mismatches=0, missing_reorder=100):
    return {
        "summary": {"duplicate_primary_keys": duplicates, "foreign_key_orphans": orphans},
        "checks": {
            "order_amount_mismatches": order_mismatches,
            "item_amount_mismatches": item_mismatches,
            "missing_reorder_point_pct": missing_reorder,
        },
    }


class QualityGateTest(unittest.TestCase):
    def setUp(self):
        self.rules = Path(__file__).resolve().parents[2] / "metadata" / "quality_rules.json"

    def test_warning_is_reported_but_does_not_block(self):
        results = evaluate_quality_gates(_report(), self.rules)
        warning = next(result for result in results if result["severity"] == "WARNING")
        self.assertFalse(warning["passed"])

    def test_critical_rule_blocks_pipeline_and_exposes_results(self):
        with self.assertRaises(QualityGateError) as raised:
            evaluate_quality_gates(_report(duplicates=1), self.rules)
        self.assertTrue(any(result["rule_id"] == "DQ-PK-001" for result in raised.exception.results))

    def test_unknown_operator_is_rejected(self):
        with TemporaryDirectory() as temporary:
            rules = Path(temporary) / "rules.json"
            rules.write_text(json.dumps({"rules": [{
                "id": "bad", "description": "bad", "metric": "summary.duplicate_primary_keys",
                "operator": "contains", "threshold": 0, "severity": "ERROR"
            }]}), encoding="utf-8")
            with self.assertRaises(KeyError):
                evaluate_quality_gates(_report(), rules)
