import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import update_fluids


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class UpdateFeedTests(unittest.TestCase):
    def test_crossref_feed_preserves_group_and_only_requests_articles(self):
        payload = {
            "message": {
                "items": [
                    {
                        "type": "journal-article",
                        "title": ["A Navier-Stokes result"],
                        "author": [{"given": "Ada", "family": "Analyst"}],
                        "abstract": "",
                        "DOI": "10.1234/example",
                        "published": {"date-parts": [[2026, 8, 20]]},
                    }
                ]
            }
        }
        feed = {
            "name": "Test Top Journal",
            "url": "1088-6834",
            "type": "crossref_journal",
            "source_group": "top-general-math",
        }

        with patch.object(update_fluids.time, "sleep"), patch.object(
            update_fluids.urllib.request,
            "urlopen",
            return_value=FakeResponse(payload),
        ) as urlopen:
            papers = update_fluids.fetch_feed(feed)

        request_url = urlopen.call_args.args[0].full_url
        self.assertIn("filter=type%3Ajournal-article", request_url)
        self.assertEqual(
            urlopen.call_args.args[0].get_header("User-agent"),
            "Fluid-Papers-Tracker/1.0",
        )
        self.assertEqual(papers[0]["source"], "Test Top Journal")
        self.assertEqual(papers[0]["source_group"], "top-general-math")
        self.assertEqual(papers[0]["title"], "A Navier-Stokes result")

    def test_main_persists_the_source_group_in_fluids_json(self):
        paper = {
            "title": "A Navier-Stokes result",
            "authors": "Ada Analyst",
            "date": "2026-08-20",
            "source": "Test Top Journal",
            "source_group": "top-general-math",
            "link": "https://doi.org/10.1234/example",
            "abstract_en": "A fluid result.",
        }
        feed = {
            "name": "Test Top Journal",
            "url": "1088-6834",
            "type": "crossref_journal",
            "source_group": "top-general-math",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            old_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                with patch.object(update_fluids, "FEEDS", [feed]), patch.object(
                    update_fluids, "fetch_feed", return_value=[paper]
                ), patch.object(
                    update_fluids, "ai_paper_filter", return_value=True
                ), patch.object(
                    update_fluids, "translate_to_zh", return_value="中文摘要"
                ), patch.object(
                    update_fluids, "create_markdown", return_value="paper.md"
                ):
                    update_fluids.main()

                with open("fluids.json", encoding="utf-8") as output:
                    saved_papers = json.load(output)
            finally:
                os.chdir(old_cwd)

        self.assertEqual(saved_papers[0]["source"], "Test Top Journal")
        self.assertEqual(saved_papers[0]["source_group"], "top-general-math")


if __name__ == "__main__":
    unittest.main()
