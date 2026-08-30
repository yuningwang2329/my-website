import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const read = (path) => readFileSync(path, 'utf8');
const readBrowser = () => read('literature-browser.js');

test('homepage does not load or typeset MathJax', () => {
  const homepage = read('index.html');
  const browser = readBrowser();

  assert.doesNotMatch(homepage, /tex-chtml\.js/);
  assert.doesNotMatch(homepage, /MathJax\.typesetPromise/);
  assert.doesNotMatch(browser, /MathJax/);
});

test('paper reader renders a stable-id summary without Markdown or external runtimes', () => {
  const reader = read('post.html');

  assert.match(reader, /urlParams\.get\('id'\)/);
  assert.match(reader, /fetch\('literature-manifest\.json'\)/);
  assert.match(reader, /\.textContent\s*=/);
  assert.match(reader, /打开原文/);
  assert.doesNotMatch(reader, /marked\.min\.js/);
  assert.doesNotMatch(reader, /MathJax/);
  assert.doesNotMatch(reader, /cdn\./);
  assert.doesNotMatch(reader, /\.innerHTML\s*=/);
});

test('homepage starts from the lightweight current index and offers historical archives', () => {
  const homepage = read('index.html');
  const browser = readBrowser();

  assert.match(homepage, /<script src="literature-browser\.js"><\/script>/);
  assert.match(browser, /fetch\('fluids-index\.json'\)/);
  assert.doesNotMatch(browser, /fetch\('fluids\.json'\)/);
  assert.match(homepage, /最近 90 天/);
  assert.match(homepage, /历史归档/);
  assert.match(homepage, /id="archive-year-filters"/);
  assert.match(browser, /function loadArchiveYear\(year\)/);
  assert.match(browser, /encodeURIComponent\(p\.id\)/);
});

test('homepage shows canonical generation and source-health metadata', () => {
  const homepage = read('index.html');
  const browser = readBrowser();

  assert.match(homepage, /id="subscription-status"/);
  assert.match(browser, /function renderSubscriptionStatus\(/);
  assert.match(browser, /failed_ids/);
  assert.match(browser, /生成于/);
});

test('homepage migrates legacy local reading state from filenames to stable IDs', () => {
  const browser = readBrowser();

  assert.match(browser, /function migrateLegacyLocalState\(papers\)/);
  assert.match(browser, /paper\.filename/);
  assert.match(browser, /migrateLegacyLocalState\(currentPapers\)/);
  assert.match(browser, /localStorage\.setItem\('fluids_stars'/);
});

test('canonical status and plain-text detail pages have local responsive styles', () => {
  const stylesheet = read('style.css');

  assert.match(stylesheet, /\.subscription-status\s*\{/);
  assert.match(stylesheet, /\.subscription-status\.degraded\s*\{/);
  assert.match(stylesheet, /\.paper-detail\s*\{/);
  assert.match(stylesheet, /\.detail-abstract\s*\{/);
  assert.match(stylesheet, /\.original-paper-link\s*\{/);
});

test('homepage provides an accessible mobile filter disclosure', () => {
  const homepage = read('index.html');
  const browser = readBrowser();

  assert.match(homepage, /id="mobile-filter-toggle"/);
  assert.match(homepage, /aria-controls="mobile-filter-panel"/);
  assert.match(homepage, /aria-expanded="false"/);
  assert.match(homepage, /onclick="toggleMobileFilters\(this\)"/);
  assert.match(browser, /function toggleMobileFilters\(button\)/);
});

test('mobile rules collapse only the filter sidebar by default', () => {
  const stylesheet = read('style.css');

  assert.match(stylesheet, /@media \(max-width: 768px\)[\s\S]*\.fluids-sidebar\s*\{[\s\S]*display:\s*none/);
  assert.match(stylesheet, /\.fluids-sidebar\.mobile-filters-open\s*\{[\s\S]*display:\s*block/);
  assert.match(stylesheet, /@media \(min-width: 769px\)[\s\S]*\.mobile-filter-toggle\s*\{[\s\S]*display:\s*none/);
});

test('homepage exposes three stable journal-group filters', () => {
  const homepage = read('index.html');
  const browser = readBrowser();

  assert.match(homepage, /id="source-group-filters"/);
  assert.match(browser, /const JOURNAL_GROUPS = \[/);
  assert.match(browser, /id: 'math-fluid-pde'/);
  assert.match(browser, /id: 'top-general-math'/);
  assert.match(browser, /id: 'high-general-math'/);
  assert.match(browser, /let filterSourceGroup = null/);
  assert.match(browser, /function sourceGroupForPaper\(paper\)/);
  assert.match(browser, /filterSourceGroup && sourceGroupForPaper\(p\) !== filterSourceGroup/);
});

test('homepage group filter preserves the real journal as paper metadata', () => {
  const browser = readBrowser();

  assert.match(browser, /meta\.textContent = paper\.source \+ ' · ' \+ paper\.date/);
  assert.doesNotMatch(browser, /meta\.textContent = sourceGroupForPaper\(paper\)/);
});

const JOURNAL_GROUP_IDS = new Set([
  'math-fluid-pde',
  'top-general-math',
  'high-general-math',
]);

const LEGACY_MATH_FLUID_SOURCES = [
  'Arxiv (math.AP)',
  'Appl. Math. Lett.',
  'Arch. Ration. Mech. Anal.',
  'Commun. Math. Phys.',
  'Commun. Pure Appl. Math.',
  'Calc. Var. Partial Differ. Equ.',
  'J. Differ. Equ.',
  'J. Funct. Anal.',
  'SIAM J. Math. Anal.',
  'J. Math. Pures Appl.',
];

test('homepage classifies every current paper through its source group or a legacy fallback', () => {
  const browser = readBrowser();
  const currentPapers = JSON.parse(read('fluids.json'));

  assert.match(
    browser,
    /return paper\.source_group \|\| LEGACY_SOURCE_GROUPS\[paper\.source\] \|\| null;/,
  );

  for (const paper of currentPapers) {
    if (paper.source_group) {
      assert.ok(
        JOURNAL_GROUP_IDS.has(paper.source_group),
        `unknown source group for ${paper.source}: ${paper.source_group}`,
      );
      continue;
    }

    const escaped = paper.source.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    assert.match(browser, new RegExp(`'${escaped}': 'math-fluid-pde'`));
  }
});

test('homepage retains legacy math-fluid source fallbacks', () => {
  const browser = readBrowser();

  for (const source of LEGACY_MATH_FLUID_SOURCES) {
    const escaped = source.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    assert.match(browser, new RegExp(`'${escaped}': 'math-fluid-pde'`));
  }
});
