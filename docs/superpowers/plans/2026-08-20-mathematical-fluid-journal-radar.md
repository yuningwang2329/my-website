# Mathematical Fluid Journal Radar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add high-signal mathematical-fluid and general-mathematics journals to the automatic subscription pipeline, with provenance-safe journal-group filtering on the homepage.

**Architecture:** Move the feed catalog and small testable Crossref/keyword helpers into a dependency-free Python module. The updater imports that catalog, persists each paper’s optional `source_group`, and keeps its real journal `source`. The static homepage adds a three-item group filter with a legacy source-name fallback, so existing papers remain visible without rewriting old data.

**Tech Stack:** Python 3.10 standard library plus existing `feedparser`/`deep-translator`, static HTML/CSS/vanilla JavaScript, Node.js built-in test runner, Python `unittest`, GitHub Actions, GitHub Pages.

## Global Constraints

- Do not change paper titles, links, `source`, Markdown rendering, or the 90-day homepage/archive split.
- Use `source_group` only as an optional internal filter key; cards and detail pages must continue to show the real `source`.
- Define exactly three stable group IDs: `math-fluid-pde`, `top-general-math`, and `high-general-math`.
- Add 18 verified journals in addition to the existing 10 sources; use official RSS for PLMS, JLMS, and Advances in Mathematics, and Crossref for the remaining verified journals.
- Crossref work-list requests must include `filter=type:journal-article`.
- Add no runtime frontend dependency or additional homepage fetch.

---

### Task 1: Lock the source catalog and fallback semantics with failing Python tests

**Files:**
- Create: `tests/test_source_catalog.py`
- Modify: none

**Interfaces:**
- Consumes: future `scripts/source_catalog.py` exports `FEEDS`, `GROUP_IDS`, `build_crossref_works_url`, `source_group_for_source`, and `matches_fluid_fallback`.
- Produces: dependency-free regression tests for source membership, grouping, Crossref query parameters, and new fluid-keyword coverage.

- [ ] **Step 1: Write the failing catalog tests**

```python
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
```

- [ ] **Step 2: Run the test to verify the intended red state**

Run: `python3 -m unittest tests/test_source_catalog.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'source_catalog'` because the catalog module has not yet been created.

### Task 2: Create the testable source catalog and update the updater to use it

**Files:**
- Create: `scripts/source_catalog.py`
- Modify: `scripts/update_fluids.py:1-145, 233-320, 365-405`
- Test: `tests/test_source_catalog.py`

**Interfaces:**
- Consumes: the test contract from Task 1.
- Produces: `FEEDS`, `GROUP_IDS`, `build_crossref_works_url(issn: str, rows: int = 15) -> str`, `source_group_for_source(source: str) -> str | None`, and `matches_fluid_fallback(title: str, abstract: str) -> bool`.

- [ ] **Step 1: Add the `source_catalog.py` helper contract**

```python
from urllib.parse import urlencode

GROUP_IDS = ("math-fluid-pde", "top-general-math", "high-general-math")

def build_crossref_works_url(issn, rows=15):
    query = urlencode({
        "filter": "type:journal-article",
        "sort": "published",
        "order": "desc",
        "rows": rows,
    })
    return f"https://api.crossref.org/journals/{issn}/works?{query}"

def source_group_for_source(source):
    return SOURCE_GROUP_BY_NAME.get(source)

def matches_fluid_fallback(title, abstract):
    text = f"{title} {abstract}".lower()
    return not any(word in text for word in EXCLUDE_KEYWORDS) and any(
        word in text for word in FALLBACK_KEYWORDS
    )
```

Populate `FEEDS` with the existing ten sources and the following exactly named new records (each record also includes the group and the type shown):

| Name | URL / ISSN | Type | Group |
| --- | --- | --- | --- |
| `J. Math. Fluid Mech.` | `1422-6952` | `crossref_journal` | `math-fluid-pde` |
| `Ann. Inst. H. Poincaré C Anal. Non Linéaire` | `1873-1430` | `crossref_journal` | `math-fluid-pde` |
| `Analysis & PDE` | `1948-206X` | `crossref_journal` | `math-fluid-pde` |
| `Nonlinearity` | `1361-6544` | `crossref_journal` | `math-fluid-pde` |
| `Ann. of Math.` | `0003-486X` | `crossref_journal` | `top-general-math` |
| `Acta Math.` | `1871-2509` | `crossref_journal` | `top-general-math` |
| `Invent. Math.` | `1432-1297` | `crossref_journal` | `top-general-math` |
| `J. Amer. Math. Soc.` | `1088-6834` | `crossref_journal` | `top-general-math` |
| `Publ. Math. IHÉS` | `1618-1913` | `crossref_journal` | `top-general-math` |
| `Proc. Lond. Math. Soc.` | `https://londmathsoc.onlinelibrary.wiley.com/feed/1460244x/most-recent` | `standard_rss` | `high-general-math` |
| `J. Lond. Math. Soc.` | `https://londmathsoc.onlinelibrary.wiley.com/feed/14697750/most-recent` | `standard_rss` | `high-general-math` |
| `Duke Math. J.` | `1547-7398` | `crossref_journal` | `high-general-math` |
| `J. Eur. Math. Soc.` | `1435-9863` | `crossref_journal` | `high-general-math` |
| `Ann. Sci. Éc. Norm. Supér.` | `1873-2151` | `crossref_journal` | `high-general-math` |
| `Adv. Math.` | `https://rss.sciencedirect.com/publication/science/00018708` | `standard_rss` | `high-general-math` |
| `J. Reine Angew. Math.` | `1435-5345` | `crossref_journal` | `high-general-math` |
| `Selecta Math.` | `1420-9020` | `crossref_journal` | `high-general-math` |
| `Forum Math. Pi` | `2050-5086` | `crossref_journal` | `high-general-math` |

Define `SOURCE_GROUP_BY_NAME` from `FEEDS`. Keep the existing fallback terms and append: `non-newtonian`, `non newtonian`, `viscoelastic`, `multiphase`, `two-phase`, `two phase`, and `porous media`.

- [ ] **Step 2: Replace updater-local configuration with catalog imports and helper calls**

At the imports in `scripts/update_fluids.py`, add:

```python
from source_catalog import FEEDS, build_crossref_works_url, matches_fluid_fallback
```

Delete the old `FEEDS`, local fallback keyword list, and local exclusion keyword list. In both existing fallback branches of `ai_paper_filter`, replace their current keyword logic with:

```python
return matches_fluid_fallback(title, abstract)
```

Replace Crossref URL construction with:

```python
cr_url = build_crossref_works_url(url)
```

Before `fetch_feed` returns, attach each feed group without changing the source:

```python
for paper in papers:
    paper["source_group"] = feed_config["source_group"]
return papers
```

When creating each `new_papers_data` record, add:

```python
"source_group": p["source_group"],
```

- [ ] **Step 3: Run the catalog test to verify green state**

Run: `python3 -m unittest tests/test_source_catalog.py -v`

Expected: all five tests pass; no third-party Python dependency is needed by the catalog test.

### Task 3: Lock the homepage group-filter contract with failing Node tests

**Files:**
- Modify: `tests/homepage-performance.test.mjs`
- Modify: none other in this task

**Interfaces:**
- Consumes: future `index.html` constants `JOURNAL_GROUPS`, `LEGACY_SOURCE_GROUPS`, `filterSourceGroup`, and `sourceGroupForPaper`.
- Produces: static regression tests that guarantee group controls and provenance rendering stay present.

- [ ] **Step 1: Append the failing homepage tests**

```javascript
test('homepage exposes three stable journal-group filters', () => {
  const homepage = read('index.html');

  assert.match(homepage, /id="source-group-filters"/);
  assert.match(homepage, /const JOURNAL_GROUPS = \[/);
  assert.match(homepage, /id: 'math-fluid-pde'/);
  assert.match(homepage, /id: 'top-general-math'/);
  assert.match(homepage, /id: 'high-general-math'/);
  assert.match(homepage, /let filterSourceGroup = null/);
  assert.match(homepage, /function sourceGroupForPaper\(paper\)/);
  assert.match(homepage, /filterSourceGroup && sourceGroupForPaper\(p\) !== filterSourceGroup/);
});

test('homepage group filter preserves the real journal as paper metadata', () => {
  const homepage = read('index.html');

  assert.match(homepage, /meta\.textContent = p\.source \+ ' · ' \+ p\.date/);
  assert.doesNotMatch(homepage, /meta\.textContent = sourceGroupForPaper\(p\)/);
});
```

- [ ] **Step 2: Run the tests to verify the intended red state**

Run: `node --test tests/homepage-performance.test.mjs`

Expected: the two new group-filter tests fail because no group sidebar or group state exists; the four pre-existing homepage tests pass.

### Task 4: Implement homepage group filtering without increasing page-load cost

**Files:**
- Modify: `index.html:35-81, 106-345`
- Test: `tests/homepage-performance.test.mjs`

**Interfaces:**
- Consumes: `source_group` emitted by Task 2 and the legacy source mapping embedded in the homepage.
- Produces: static journal-group controls that combine with existing topic, journal, month, and starred filters.

- [ ] **Step 1: Add the static group section after the topic section**

Insert this markup before the existing periodical/month tab group:

```html
<div class="folder-group" style="margin-top: 24px;">
    <div class="folder-header">期刊组</div>
    <ul class="folder-list" id="source-group-filters"></ul>
</div>
```

- [ ] **Step 2: Add group constants and state alongside current filter state**

```javascript
const JOURNAL_GROUPS = [
    { id: 'math-fluid-pde', label: '数学流体与非线性 PDE' },
    { id: 'top-general-math', label: '顶级综合数学' },
    { id: 'high-general-math', label: '综合数学高刊' },
];
const LEGACY_SOURCE_GROUPS = {
    'Arxiv (math.AP)': 'math-fluid-pde',
    'Appl. Math. Lett.': 'math-fluid-pde',
    'Arch. Ration. Mech. Anal.': 'math-fluid-pde',
    'Commun. Math. Phys.': 'math-fluid-pde',
    'Commun. Pure Appl. Math.': 'math-fluid-pde',
    'Calc. Var. Partial Differ. Equ.': 'math-fluid-pde',
    'J. Differ. Equ.': 'math-fluid-pde',
    'J. Funct. Anal.': 'math-fluid-pde',
    'SIAM J. Math. Anal.': 'math-fluid-pde',
    'J. Math. Pures Appl.': 'math-fluid-pde',
};
let filterSourceGroup = null;

function sourceGroupForPaper(paper) {
    return paper.source_group || LEGACY_SOURCE_GROUPS[paper.source] || null;
}
```

- [ ] **Step 3: Add group-filter handlers and apply the predicate**

```javascript
function toggleSourceGroupFilter(groupId) {
    filterSourceGroup = filterSourceGroup === groupId ? null : groupId;
    render();
}

function clearSourceGroupFilter() {
    filterSourceGroup = null;
    render();
}
```

Place this predicate directly before the existing journal/month predicates in `getPapersToRender`:

```javascript
if (filterSourceGroup && sourceGroupForPaper(p) !== filterSourceGroup) return false;
```

- [ ] **Step 4: Render permanent group links and the group filter tag**

In `render()`, calculate group counts from `sourceGroupForPaper(p)`. Clear and rebuild `#source-group-filters` on every render so counts and active state cannot become stale. For each `JOURNAL_GROUPS` item, create the same `<a class="folder-link">`/count structure used for individual journals; display the item even when its count is zero. If a group is selected, add a `filter-tag` with the group label and a close action calling `clearSourceGroupFilter()`.

- [ ] **Step 5: Run Node tests to verify green state**

Run: `node --test tests/homepage-performance.test.mjs`

Expected: all six tests pass, including both new group-filter tests.

### Task 5: Guard the scheduled workflow and run complete local regression checks

**Files:**
- Modify: `.github/workflows/update_fluids.yml:22-35`
- Test: `tests/test_source_catalog.py`, `tests/homepage-performance.test.mjs`

**Interfaces:**
- Consumes: working Python catalog tests and Node homepage tests.
- Produces: an automated update workflow that validates configuration and UI contracts before writing or pushing paper data.

- [ ] **Step 1: Add the workflow regression-test step after dependency installation**

```yaml
- name: Run subscription regression tests
  run: |
    python -m unittest tests/test_source_catalog.py -v
    node --test tests/homepage-performance.test.mjs
```

- [ ] **Step 2: Run all local checks**

Run:

```bash
python3 -m unittest tests/test_source_catalog.py -v
node --test tests/homepage-performance.test.mjs
python3 -m py_compile scripts/source_catalog.py scripts/update_fluids.py
git diff --check
```

Expected: all Python and Node tests pass, both Python modules compile, and `git diff --check` emits no output.

### Task 6: Verify all source endpoints and inspect final output before commit

**Files:**
- Verify: `scripts/source_catalog.py`, `scripts/update_fluids.py`, `fluids.json`, `.github/workflows/update_fluids.yml`

**Interfaces:**
- Consumes: the completed catalog, updater, frontend, and workflow.
- Produces: fresh endpoint evidence and a clean implementation diff ready for commit.

- [ ] **Step 1: Execute a read-only endpoint probe using the catalog**

Run a Python snippet that imports `FEEDS`, makes each `crossref_journal` request with `build_crossref_works_url`, fetches each RSS URL, and exits nonzero if an endpoint fails HTTP 200, has no entries/items, or returns an empty Crossref title. The probe must not write `fluids.json`.

- [ ] **Step 2: Perform data integrity checks**

```bash
python3 -m json.tool fluids.json >/dev/null
for f in $(jq -r '.[].filename' fluids.json); do test -f "fluids/$f" || exit 1; done
```

Expected: valid JSON and every indexed current paper has a Markdown file.

- [ ] **Step 3: Inspect requirements against the final diff**

```bash
git diff --check
git diff -- scripts/source_catalog.py scripts/update_fluids.py index.html .github/workflows/update_fluids.yml tests
git status --short --branch
```

Verify: all 28 feed names are unique; the five top-general journals have the correct group; all three group IDs render; paper metadata still uses `p.source`; Crossref filtering is present; and workflow tests run before the updater.

- [ ] **Step 4: Commit only after all checks pass**

```bash
git add scripts/source_catalog.py scripts/update_fluids.py index.html .github/workflows/update_fluids.yml tests/homepage-performance.test.mjs tests/test_source_catalog.py docs/superpowers/specs/2026-08-20-mathematical-fluid-journal-radar-design.md docs/superpowers/plans/2026-08-20-mathematical-fluid-journal-radar.md
git commit -m "feat: add mathematical fluid journal radar"
```
