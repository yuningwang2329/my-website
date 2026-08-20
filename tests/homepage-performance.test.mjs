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

test('homepage places every existing paper source in the math-fluid legacy group', () => {
  const homepage = read('index.html');
  const currentSources = new Set(JSON.parse(read('fluids.json')).map((paper) => paper.source));

  for (const source of currentSources) {
    const escaped = source.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    assert.match(homepage, new RegExp(`'${escaped}': 'math-fluid-pde'`));
  }
});
