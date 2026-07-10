import glob

old_btn = '<button id="search-btn" class="search-btn">搜索 <kbd>⌘K</kbd></button>'
new_btn = '<button id="search-btn" class="search-btn" aria-label="搜索"><svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg></button>'

old_overlay = """    <div id="search-overlay" class="search-overlay">
        <div class="search-box">
            <input id="search-input" class="search-input" type="text" placeholder="搜索笔记、出版物…" autocomplete="off">
            <div id="search-results" class="search-results"></div>
        </div>
    </div>"""

new_overlay = """    <div id="search-overlay" class="search-overlay">
        <div class="search-panel">
            <div class="search-box">
                <div class="search-input-wrapper">
                    <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                    <input id="search-input" class="search-input" type="text" placeholder="搜索" autocomplete="off">
                </div>
                <div id="search-label" class="search-results-label">快速链接</div>
                <div id="search-results" class="search-results"></div>
            </div>
        </div>
    </div>"""

for filepath in glob.glob("*.html"):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(old_btn, new_btn)
    content = content.replace(old_overlay, new_overlay)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("HTML files updated.")
