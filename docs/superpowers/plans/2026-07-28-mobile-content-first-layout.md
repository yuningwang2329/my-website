# Mobile Content-First Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** On phone-sized screens, show the paper list first and reveal the existing filters only when the visitor requests them.

**Architecture:** Keep the desktop sidebar unchanged. Add one accessible disclosure button before the existing sidebar, reuse the sidebar as its controlled panel on mobile, and give it a single mobile-only open class. A small inline function owns only disclosure state; all existing filter and reading-state functions remain untouched.

**Tech Stack:** Static HTML, CSS media queries, vanilla JavaScript, Node built-in test runner.

## Global Constraints

- Do not add a framework, package, network request, or external dependency.
- Desktop widths above 768px must retain the permanently visible sidebar.
- At 390px wide, the first visible content after the filter button must be the paper-list heading and papers, not journal rows.
- The disclosure button must use `aria-controls` and keep `aria-expanded` synchronized with the panel state.
- Existing journal, month, topic, starred, read, and “mark all read” behavior must remain unchanged.

---

### Task 1: Lock the mobile disclosure contract with tests

**Files:**
- Modify: `tests/homepage-performance.test.mjs`

**Interfaces:**
- Consumes: homepage markup from `index.html` and responsive rules from `style.css`.
- Produces: regression tests that require an accessible mobile filter button and a mobile-only collapsed sidebar rule.

- [x] **Step 1: Write the failing structural tests**

Append these tests to `tests/homepage-performance.test.mjs`:

```js
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
```

- [x] **Step 2: Run the tests to verify they fail for the missing feature**

Run:

```bash
node --test tests/homepage-performance.test.mjs
```

Expected: FAIL because `mobile-filter-toggle` and the new responsive rules do not exist yet; the two existing performance tests still pass.

### Task 2: Implement the content-first mobile disclosure

**Files:**
- Modify: `index.html:24-74`
- Modify: `index.html:140-172`
- Modify: `style.css:1155-1188`

**Interfaces:**
- Consumes: `#mobile-filter-toggle` button, `#mobile-filter-panel` sidebar, and `toggleMobileFilters(button)` from Task 1.
- Produces: a mobile-only disclosure whose class and ARIA state match after each click.

- [x] **Step 1: Add the disclosure control and controlled-panel identifier**

Immediately inside `<div class="fluids-layout">`, before the `<aside>`, add:

```html
<button
    id="mobile-filter-toggle"
    class="mobile-filter-toggle"
    type="button"
    aria-controls="mobile-filter-panel"
    aria-expanded="false"
    onclick="toggleMobileFilters(this)">
    筛选文献
</button>
```

Change the sidebar opening tag to:

```html
<aside id="mobile-filter-panel" class="fluids-sidebar">
```

- [x] **Step 2: Add the smallest state function without changing filter logic**

Place this function above `switchFolder` in `index.html`:

```js
function toggleMobileFilters(button) {
    const panel = document.getElementById('mobile-filter-panel');
    const isOpen = panel.classList.toggle('mobile-filters-open');

    button.setAttribute('aria-expanded', String(isOpen));
    button.textContent = isOpen ? '收起筛选' : '筛选文献';
}
```

- [x] **Step 3: Replace the existing 768px sidebar section with disclosure styles**

Within the existing `@media (max-width: 768px)` block, keep the column layout and add these rules after `.fluids-layout`:

```css
.mobile-filter-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 44px;
    padding: 10px 14px;
    color: var(--text);
    font: inherit;
    font-size: 0.9rem;
    font-weight: 600;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    cursor: pointer;
}

.fluids-sidebar {
    display: none;
    flex: none;
    width: 100%;
    position: static;
    max-height: none;
    padding-bottom: 8px;
}

.fluids-sidebar.mobile-filters-open {
    display: block;
}
```

Keep the existing mobile `.folder-group` and `.folder-list` rules so the expanded panel retains touch scrolling. Add this desktop guard outside the mobile query:

```css
@media (min-width: 769px) {
    .mobile-filter-toggle {
        display: none;
    }
}
```

- [x] **Step 4: Run the regression suite to verify it is green**

Run:

```bash
node --test tests/homepage-performance.test.mjs
```

Expected: PASS with four passing tests and no failures.

- [x] **Step 5: Verify the live interactions at both responsive breakpoints**

Run a local static server from `/Users/wangyuning/Desktop/资料/Works/Misc/Website`, then verify in a browser:

1. At 390×844, the initial sidebar is hidden, the button says “筛选文献”, and the visible paper heading is above the fold.
2. Click the button: it changes to “收起筛选”, `aria-expanded` becomes `true`, and journal/month controls are visible.
3. Click a journal filter, then collapse and reopen: the selected list remains filtered.
4. At 1280px wide, the button is absent and the sidebar is visible without interaction.
5. Open one paper detail page and confirm it still renders.

- [ ] **Step 6: Commit the completed mobile interaction**

```bash
git add index.html style.css tests/homepage-performance.test.mjs
git commit -m "feat: prioritize papers on mobile"
```

### Task 3: Publish and verify the deployed site

**Files:**
- No source changes expected.

**Interfaces:**
- Consumes: the commit from Task 2 and the existing GitHub Pages deployment workflow.
- Produces: a deployed version whose mobile contract matches the local verification.

- [ ] **Step 1: Push the verified commit**

Run:

```bash
git push origin main
```

Expected: the remote `main` branch advances by the mobile-layout commit.

- [ ] **Step 2: Wait for the GitHub Pages deployment to complete successfully**

Open the repository Actions page and verify the deployment associated with the pushed commit has a successful status.

- [ ] **Step 3: Re-run the 390px mobile checks against the public URL**

Visit `https://yuningwang2329.github.io/my-website/` at 390×844 and confirm the initial paper-first view, filter expansion, and paper-detail navigation match Task 2.

- [ ] **Step 4: Record completion evidence**

Report the test result, public deployment result, and the exact public URL. Do not claim release success unless both the local test suite and the Pages deployment are successful.
