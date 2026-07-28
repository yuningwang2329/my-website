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
