import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sync_canonical_literature import CanonicalSyncError, sync_canonical_artifacts


def _sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def _paper(identifier, *, date="2026-08-20"):
    return {
        "id": identifier,
        "title": f"A fluid result {identifier}",
        "authors": "Ada Analyst",
        "date": date,
        "source": "J. Math. Fluid Mech.",
        "source_group": "math-fluid-pde",
        "link": f"https://doi.org/10.1000/{identifier}",
        "doi": f"10.1000/{identifier}",
        "arxiv_url": "",
        "filename": f"{identifier.replace(':', '-').replace('/', '-')}.md",
        "abstract_en": "A long English abstract that must not be in the home index.",
        "summary_zh": "首页索引不应携带这段中文摘要。",
        "topic": "流体方程",
        "topic_tags": ["navier-stokes"],
        "tags": ["navier-stokes"],
        "relevance": "core",
    }


class CanonicalMirrorTests(unittest.TestCase):
    def _write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
        path.write_bytes(payload)
        return payload

    def _manifest(self, active_payload, archive_payload):
        return {
            "schema_version": 1,
            "generation_id": "generation-20260830",
            "generated_at": "2026-08-30T02:00:00Z",
            "policy_version": "2026.08.30",
            "window_days": 90,
            "counts": {"current": 2, "archived": 1, "review": 0},
            "sources": {"total": 29, "succeeded": 28, "failed_ids": ["jfa"]},
            "current": {
                "path": "fluids.json",
                "count": 2,
                "sha256": _sha256(active_payload),
                "bytes": len(active_payload),
            },
            "archives": [
                {
                    "year": 2025,
                    "path": "archive/archive_2025.json",
                    "count": 1,
                    "sha256": _sha256(archive_payload),
                    "bytes": len(archive_payload),
                }
            ],
        }

    def test_sync_accepts_hashed_canonical_data_and_builds_a_small_home_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical_root = root / "canonical"
            target_root = root / "website"
            active_payload = self._write_json(
                canonical_root / "fluids.json", [_paper("doi:10.1000/current-a"), _paper("doi:10.1000/current-b")]
            )
            archive_payload = self._write_json(
                canonical_root / "archive" / "archive_2025.json",
                [_paper("doi:10.1000/archive-a", date="2025-03-01")],
            )
            self._write_json(
                canonical_root / "literature-manifest.json",
                self._manifest(active_payload, archive_payload),
            )

            result = sync_canonical_artifacts(
                canonical_root,
                target_root,
                now=datetime(2026, 8, 30, 3, 0, tzinfo=timezone.utc),
            )

            index = json.loads((target_root / "fluids-index.json").read_text(encoding="utf-8"))
            copied_manifest = json.loads((target_root / "literature-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(result.active_count, 2)
            self.assertEqual(result.archive_count, 1)
            self.assertEqual(copied_manifest["generation_id"], "generation-20260830")
            self.assertEqual([paper["id"] for paper in index["papers"]], ["doi:10.1000/current-a", "doi:10.1000/current-b"])
            self.assertEqual(index["generation_id"], "generation-20260830")
            self.assertEqual(index["papers"][0]["filename"], "doi-10.1000-current-a.md")
            self.assertEqual(
                index["archives"],
                [{"year": 2025, "path": "archive/archive_2025.json", "count": 1}],
            )
            self.assertNotIn("abstract_en", index["papers"][0])
            self.assertNotIn("summary_zh", index["papers"][0])
            self.assertTrue((target_root / "fluids.json").is_file())
            self.assertTrue((target_root / "archive" / "archive_2025.json").is_file())

    def test_sync_rejects_a_bad_hash_without_overwriting_existing_site_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical_root = root / "canonical"
            target_root = root / "website"
            old_data = b'[{"id":"old-site-paper"}]'
            target_root.mkdir()
            (target_root / "fluids.json").write_bytes(old_data)

            active_payload = self._write_json(canonical_root / "fluids.json", [_paper("doi:10.1000/current-a")])
            archive_payload = self._write_json(
                canonical_root / "archive" / "archive_2025.json",
                [_paper("doi:10.1000/archive-a", date="2025-03-01")],
            )
            manifest = self._manifest(active_payload + b"tampered", archive_payload)
            manifest["current"]["count"] = 1
            self._write_json(canonical_root / "literature-manifest.json", manifest)

            with self.assertRaises(CanonicalSyncError):
                sync_canonical_artifacts(
                    canonical_root,
                    target_root,
                    now=datetime(2026, 8, 30, 3, 0, tzinfo=timezone.utc),
                )

            self.assertEqual((target_root / "fluids.json").read_bytes(), old_data)

    def test_sync_rejects_incomplete_records_or_wrong_byte_sizes_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical_root = root / "canonical"
            target_root = root / "website"
            old_data = b'[{"id":"old-site-paper"}]'
            target_root.mkdir()
            (target_root / "fluids.json").write_bytes(old_data)

            current_paper = _paper("doi:10.1000/current-a")
            current_paper.pop("doi")
            active_payload = self._write_json(
                canonical_root / "fluids.json", [current_paper]
            )
            archive_payload = self._write_json(
                canonical_root / "archive" / "archive_2025.json",
                [_paper("doi:10.1000/archive-a", date="2025-03-01")],
            )
            manifest = self._manifest(active_payload, archive_payload)
            manifest["counts"] = {"current": 1, "archived": 1, "review": 0}
            manifest["current"]["count"] = 1
            manifest["current"]["bytes"] = len(active_payload) + 1
            self._write_json(canonical_root / "literature-manifest.json", manifest)

            with self.assertRaises(CanonicalSyncError):
                sync_canonical_artifacts(
                    canonical_root,
                    target_root,
                    now=datetime(2026, 8, 30, 3, 0, tzinfo=timezone.utc),
                )

            self.assertEqual((target_root / "fluids.json").read_bytes(), old_data)

    def test_sync_refuses_a_stale_generation_without_overwriting_existing_site_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canonical_root = root / "canonical"
            target_root = root / "website"
            old_data = b'[{"id":"old-site-paper"}]'
            target_root.mkdir()
            (target_root / "fluids.json").write_bytes(old_data)

            active_payload = self._write_json(
                canonical_root / "fluids.json", [_paper("doi:10.1000/current-a")]
            )
            archive_payload = self._write_json(
                canonical_root / "archive" / "archive_2025.json",
                [_paper("doi:10.1000/archive-a", date="2025-03-01")],
            )
            manifest = self._manifest(active_payload, archive_payload)
            manifest["counts"] = {"current": 1, "archived": 1, "review": 0}
            manifest["generated_at"] = "2026-08-01T02:00:00Z"
            self._write_json(canonical_root / "literature-manifest.json", manifest)

            with self.assertRaises(CanonicalSyncError):
                sync_canonical_artifacts(
                    canonical_root,
                    target_root,
                    now=datetime(2026, 8, 30, 3, 0, tzinfo=timezone.utc),
                )

            self.assertEqual((target_root / "fluids.json").read_bytes(), old_data)


class WebsiteMirrorWorkflowTests(unittest.TestCase):
    def test_update_workflow_syncs_the_canonical_repository_after_each_production_window(self):
        workflow = (ROOT / ".github" / "workflows" / "update_fluids.yml").read_text(encoding="utf-8")

        self.assertIn("name: Canonical Literature Mirror", workflow)
        self.assertIn("repository: yuningwang2329/MySecondBrain", workflow)
        self.assertIn("path: canonical", workflow)
        for cron in ("37 21 * * *", "7 0 * * *", "43 0 * * *", "43 1 * * *"):
            self.assertIn(f"cron: '{cron}'", workflow)
        self.assertIn(
            "python scripts/sync_canonical_literature.py --canonical-root canonical --website-root .",
            workflow,
        )
        self.assertIn("python -m unittest tests.test_canonical_sync -v", workflow)
        self.assertNotIn("pip install feedparser", workflow)
        self.assertNotIn("unittest discover -s tests", workflow)
        self.assertIn("git diff --cached --quiet", workflow)
        self.assertNotIn("python scripts/update_fluids.py", workflow)
        self.assertNotIn("git add -A", workflow)

    def test_legacy_ai_sweep_is_retained_but_cannot_mutate_the_canonical_mirror(self):
        workflow = (ROOT / ".github" / "workflows" / "ai_sweep.yml").read_text(encoding="utf-8")

        self.assertIn("Legacy sweep retained for rollback", workflow)
        self.assertNotIn("python scripts/ai_sweep.py", workflow)
        self.assertNotIn("git push", workflow)


if __name__ == "__main__":
    unittest.main()
