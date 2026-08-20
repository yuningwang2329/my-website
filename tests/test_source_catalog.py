import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from source_catalog import (
    FEEDS,
    GROUP_IDS,
    build_crossref_works_url,
    matches_fluid_fallback,
    source_group_for_source,
)


class SourceCatalogTests(unittest.TestCase):
    def test_every_feed_has_one_supported_group(self):
        self.assertEqual(
            GROUP_IDS,
            ("math-fluid-pde", "top-general-math", "high-general-math"),
        )
        self.assertEqual(len(FEEDS), 28)
        self.assertTrue(all(feed["source_group"] in GROUP_IDS for feed in FEEDS))

    def test_top_general_math_group_contains_the_four_journals_and_pmihes(self):
        top_names = {
            feed["name"]
            for feed in FEEDS
            if feed["source_group"] == "top-general-math"
        }
        self.assertEqual(
            top_names,
            {
                "Ann. of Math.",
                "Acta Math.",
                "Invent. Math.",
                "J. Amer. Math. Soc.",
                "Publ. Math. IHÉS",
            },
        )

    def test_crossref_requests_only_journal_articles(self):
        url = build_crossref_works_url("1088-6834")
        query = parse_qs(urlsplit(url).query)
        self.assertEqual(query["filter"], ["type:journal-article"])
        self.assertEqual(query["sort"], ["published"])
        self.assertEqual(query["order"], ["desc"])
        self.assertEqual(query["rows"], ["15"])

    def test_known_legacy_source_is_in_the_math_fluid_group(self):
        self.assertEqual(source_group_for_source("SIAM J. Math. Anal."), "math-fluid-pde")

    def test_fallback_accepts_complex_fluid_terms(self):
        self.assertTrue(matches_fluid_fallback("Viscoelastic non-Newtonian flow", ""))
        self.assertTrue(matches_fluid_fallback("Multiphase flow through porous media", ""))


if __name__ == "__main__":
    unittest.main()
