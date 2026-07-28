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
