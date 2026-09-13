from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from retail_data_platform.governance.catalog import validate_catalog
from retail_data_platform.governance.lineage import build_lineage, write_openlineage_event
from retail_data_platform.data_engineering.ingestion import REQUIRED_COLUMNS


ROOT = Path(__file__).resolve().parents[2]


class CatalogAndLineageTest(unittest.TestCase):
    def test_catalog_is_complete_and_public_outputs_are_not_pii(self):
        datasets = validate_catalog(
            ROOT / "metadata" / "datasets.json",
            ROOT / "metadata" / "classifications.json",
        )
        raw = [dataset for dataset in datasets if dataset["layer"] == "raw"]
        public = [dataset for dataset in datasets if dataset["layer"] == "public"]
        self.assertEqual(len(raw), 24)
        self.assertEqual({dataset["name"].removeprefix("raw.") for dataset in raw}, set(REQUIRED_COLUMNS))
        self.assertTrue(public)
        self.assertTrue(all(not dataset["contains_pii"] for dataset in public))
        self.assertTrue(all(dataset["classification"] == "PUBLIC" for dataset in public))

    def test_lineage_covers_required_outputs_and_writes_openlineage(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            lineage = build_lineage(ROOT / "metadata" / "lineage.json", root / "lineage.json", "run-1")
            event = write_openlineage_event(
                root / "event.json", "run-1", lineage["job"], ["raw.orders"], ["public.dashboard"]
            )
            self.assertTrue((root / "lineage.mmd").exists())
            self.assertEqual(event["eventType"], "COMPLETE")
            self.assertEqual(event["run"]["runId"], "run-1")
            self.assertTrue(lineage["column_lineage"])

    def test_no_local_user_path_is_committed_in_governance_text(self):
        candidates = list((ROOT / "metadata").rglob("*.json")) + list((ROOT / "docs").rglob("*.md"))
        content = "\n".join(path.read_text(encoding="utf-8") for path in candidates)
        self.assertNotIn("C:\\Users\\", content)
        self.assertNotIn("@gmail.com", content.lower())
