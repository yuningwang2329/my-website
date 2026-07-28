# Homepage First-Load Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the paper-library homepage load without downloading or running MathJax, while preserving equation rendering in individual paper pages.

**Architecture:** `index.html` remains a static shell that fetches `fluids.json` and renders the paper list. `post.html` remains the only page that loads Marked and MathJax because it renders a selected Markdown paper. A Node built-in test protects this split without adding dependencies.

**Tech Stack:** Static HTML/CSS/JavaScript, Node.js built-in test runner, GitHub Pages.

## Global Constraints

- Modify only the homepage's MathJax dependency and its list-level typesetting call.
- Keep `post.html` Markdown parsing and MathJax loading unchanged.
- Do not change `fluids.json`, paper files, filters, read state, starred state, or GitHub Actions update workflows.
- Prove the final public site serves the latest `fluids.json` and that the homepage no longer requests `tex-chtml.js`.

---

### Task 1: Lock in the homepage/detail-page boundary

**Files:**
- Create: `tests/homepage-performance.test.mjs`
- Modify: `index.html:9-17,418-422`
- Verify: `post.html:9-18,55-67`

**Interfaces:**
- Consumes: homepage HTML at `index.html` and article reader at `post.html`.
- Produces: a homepage that does not reference MathJax and an article reader that still references `marked.min.js`, `tex-chtml.js`, and `MathJax.typesetPromise`.

- [x] **Step 1: Write the failing regression test**

```js
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
```

- [x] **Step 2: Run the test to verify the current homepage fails for the intended reason**

Run: `node --test tests/homepage-performance.test.mjs`

Expected: the `homepage does not load or typeset MathJax` test fails because `index.html` still contains `tex-chtml.js` and `MathJax.typesetPromise`; the reader test passes.

- [x] **Step 3: Remove the homepage-only MathJax work**

Remove this entire block from the `<head>` of `index.html`:

```html
    <script>
      MathJax = {
        tex: {
          inlineMath: [['$', '$'], ['\\(', '\\)']]
        }
      };
    </script>
    <script id="MathJax-script" async src="https://cdn.staticfile.net/mathjax/3.2.2/es5/tex-chtml.js"></script>
```

Remove this block from the end of `render()` in `index.html`:

```js
            if (window.MathJax && typeof MathJax.typesetPromise === 'function') {
                MathJax.typesetPromise([container]).catch(function(err) {
                    console.error('MathJax error:', err);
                });
            }
```

- [x] **Step 4: Run the regression test and static data integrity check**

Run:

```bash
node --test tests/homepage-performance.test.mjs
jq -e 'type == "array" and length > 0' fluids.json >/dev/null
for f in $(jq -r '.[].filename' fluids.json); do test -f "fluids/$f" || exit 1; done
git diff --check
```

Expected: both Node tests pass; `fluids.json` is a non-empty array; every indexed paper Markdown file exists; no whitespace errors are reported.

- [ ] **Step 5: Commit the focused code and regression test**

```bash
git add index.html tests/homepage-performance.test.mjs
git commit -m "perf: remove MathJax from homepage"
```

### Task 2: Verify local and public first-load behavior

**Files:**
- Verify: `index.html`, `post.html`, `fluids.json`, `tests/homepage-performance.test.mjs`

**Interfaces:**
- Consumes: the Task 1 commit and the GitHub Pages deployment triggered by `git push origin main`.
- Produces: evidence that the homepage and article reader both work and the published data is current.

- [x] **Step 1: Verify static routes locally**

Run `python3 -m http.server 8765 --bind 127.0.0.1` from the repository root. In another terminal, run:

```bash
curl --noproxy '*' -sS -o /dev/null -w 'home %{http_code}\n' http://127.0.0.1:8765/
curl --noproxy '*' -sS -o /dev/null -w 'reader %{http_code}\n' http://127.0.0.1:8765/post.html
curl --noproxy '*' -sS -o /dev/null -w 'data %{http_code}\n' http://127.0.0.1:8765/fluids.json
```

Expected: all three routes return `200`.

- [x] **Step 2: Visually inspect the desktop homepage and one paper reader page**

Open `http://127.0.0.1:8765/` and confirm the full paper list, sidebar counts, and filters render. Open one visible `post.html?file=fluids/<filename>.md` link and confirm it loads the paper title and summary.

Expected: the homepage has no console errors and the article page still renders its selected Markdown content.

- [ ] **Step 3: Push and verify the deployed resource split**

```bash
git push origin main
curl -L -sS -o /dev/null -w 'home %{http_code} %{time_total}s\n' https://yuningwang2329.github.io/my-website/
curl -L -sS -o /dev/null -w 'data %{http_code} %{time_total}s\n' https://yuningwang2329.github.io/my-website/fluids.json
curl -L -sS https://yuningwang2329.github.io/my-website/ -o /tmp/home.html
rg -n 'tex-chtml\.js|MathJax\.typesetPromise' /tmp/home.html
```

Expected: the homepage and data return `200`; the final `rg` command returns no matches (exit status `1`); the GitHub Pages run for the pushed commit finishes successfully.

- [ ] **Step 4: Commit the plan record if it changed during execution**

```bash
git add docs/superpowers/plans/2026-07-28-homepage-first-load-optimization.md
git diff --cached --quiet || git commit -m "docs: record homepage load verification"
```
