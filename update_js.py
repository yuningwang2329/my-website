import re

with open('search.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the input event listener to handle default links
old_logic = """    input.addEventListener('input', function () {
        var q = input.value.trim().toLowerCase();
        results.innerHTML = '';

        if (!q) return;"""

new_logic = """    function renderResults(items) {
        results.innerHTML = '';
        items.forEach(function (item) {
            var a = document.createElement('a');
            a.href = item.url;
            a.className = 'search-result-item';
            a.innerHTML =
                '<span class="search-result-title">' + item.title + '</span>' +
                '<span class="search-result-desc">' + item.desc + '</span>';
            results.appendChild(a);
        });
    }

    function showDefaultLinks() {
        var label = document.getElementById('search-label');
        if (label) label.textContent = '快速链接';
        // Show first 4 items as quick links
        renderResults(SEARCH_INDEX.slice(0, 4));
    }

    // Initialize with default links when opened
    btn.addEventListener('click', function (e) {
        e.preventDefault();
        overlay.classList.add('open');
        input.value = '';
        showDefaultLinks();
        setTimeout(function () { input.focus(); }, 50);
    });
    
    document.addEventListener('keydown', function (e) {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            overlay.classList.add('open');
            input.value = '';
            showDefaultLinks();
            setTimeout(function () { input.focus(); }, 50);
        }
        if (e.key === 'Escape') {
            overlay.classList.remove('open');
        }
    });

    input.addEventListener('input', function () {
        var q = input.value.trim().toLowerCase();
        var label = document.getElementById('search-label');
        
        if (!q) {
            showDefaultLinks();
            return;
        }
        
        if (label) label.textContent = '搜索结果';"""

# Note: We need to cleanly replace the listeners.
# Let's just rewrite search.js entirely, it's safer.
