from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from retail_data_platform.governance.audit import AuditRun, sha256_file


class AuditRunTest(unittest.TestCase):
    def test_completed_run_records_hashes_without_absolute_paths(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "orders.csv"
            source.write_text("id,total\n1,10.00\n", encoding="utf-8")
            artifact = root / "project" / "result.json"
            artifact.parent.mkdir()
            artifact.write_text("{}", encoding="utf-8")

            with AuditRun("test.pipeline", root / "audit") as run:
                with run.step("extract"):
                    run.add_source(source, 1)
                run.add_dataset("raw.orders", 1, ["id", "total"])
                run.add_artifact(artifact, root / "project")

            manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
            serialized = json.dumps(manifest)
            self.assertEqual(manifest["status"], "COMPLETED")
            self.assertEqual(manifest["sources"][0]["sha256"], sha256_file(source))
            self.assertEqual(manifest["artifacts"][0]["path"], "result.json")
            self.assertNotIn(str(root), serialized)

    def test_failed_run_is_closed_without_persisting_error_message(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(RuntimeError, "segredo"):
                with AuditRun("test.pipeline", root / "audit") as run:
                    with run.step("load"):
                        raise RuntimeError("segredo que não deve ser persistido")
            manifest = json.loads(run.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "FAILED")
            self.assertEqual(manifest["error"], {"type": "RuntimeError"})
            self.assertNotIn("segredo", json.dumps(manifest))
