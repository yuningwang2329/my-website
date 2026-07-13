import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

for file in html_files:
    with open(file, 'r') as f:
        content = f.read()

    # Move all local scripts to head with defer (excluding inline scripts)
    local_scripts = re.findall(r'<script src="(script\.js|search\.js)"></script>', content)
    
    # Remove them from body
    content = re.sub(r'\s*<script src="(script\.js|search\.js)"></script>', '', content)
    
    # Build head scripts
    head_scripts = ""
    for script in local_scripts:
        head_scripts += f'    <script src="{script}" defer></script>\n'
    
    # If post.html, handle CDN updates
    if file == 'post.html':
        content = content.replace('https://cdn.bootcdn.net/ajax/libs/marked/4.3.0/marked.min.js', 'https://cdn.staticfile.net/marked/4.3.0/marked.min.js')
        content = content.replace('https://cdn.bootcdn.net/ajax/libs/mathjax/3.2.2/es5/tex-chtml.js', 'https://cdn.staticfile.net/mathjax/3.2.2/es5/tex-chtml.js')
        
        # Add preconnect
        if '<link rel="preconnect" href="https://cdn.staticfile.net">' not in content:
            head_scripts = '    <link rel="preconnect" href="https://cdn.staticfile.net">\n' + head_scripts

    if head_scripts:
        content = content.replace('</head>', head_scripts + '</head>')
        
    with open(file, 'w') as f:
        f.write(content)

print("HTML optimized successfully.")
