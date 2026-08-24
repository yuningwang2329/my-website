import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const read = (path) => readFileSync(path, 'utf8');

test('homepage does not load or typeset MathJax', () => {
  const homepage = read('index.html');

  assert.doesNotMatch(homepage, /tex-chtml\.js/);
  assert.doesNotMatch(homepage, /MathJax\.typesetPromise/);
});

test('paper reader retains Markdown and equation rendering', () => {
  const reader = read('post.html');

  assert.match(reader, /marked\.min\.js/);
  assert.match(reader, /tex-chtml\.js/);
  assert.match(reader, /MathJax\.typesetPromise/);
});

test('homepage provides an accessible mobile filter disclosure', () => {
  const homepage = read('index.html');

  assert.match(homepage, /id="mobile-filter-toggle"/);
  assert.match(homepage, /aria-controls="mobile-filter-panel"/);
  assert.match(homepage, /aria-expanded="false"/);
  assert.match(homepage, /onclick="toggleMobileFilters\(this\)"/);
  assert.match(homepage, /function toggleMobileFilters\(button\)/);
});

test('mobile rules collapse only the filter sidebar by default', () => {
  const stylesheet = read('style.css');

  assert.match(stylesheet, /@media \(max-width: 768px\)[\s\S]*\.fluids-sidebar\s*\{[\s\S]*display:\s*none/);
  assert.match(stylesheet, /\.fluids-sidebar\.mobile-filters-open\s*\{[\s\S]*display:\s*block/);
  assert.match(stylesheet, /@media \(min-width: 769px\)[\s\S]*\.mobile-filter-toggle\s*\{[\s\S]*display:\s*none/);
});

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
  const homepage = read('index.html');
  const currentPapers = JSON.parse(read('fluids.json'));

  assert.match(
    homepage,
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
    assert.match(homepage, new RegExp(`'${escaped}': 'math-fluid-pde'`));
  }
});

test('homepage retains legacy math-fluid source fallbacks', () => {
  const homepage = read('index.html');

  for (const source of LEGACY_MATH_FLUID_SOURCES) {
    const escaped = source.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    assert.match(homepage, new RegExp(`'${escaped}': 'math-fluid-pde'`));
  }
});
