import os
import re

frontend_dir = r'c:\Users\Abhishek\OneDrive\Desktop\orca clone\orca\orca-frontend'
html_files = [
    'index.html',
    'dashboard.html',
    'assistant.html',
    'map.html',
    'safety.html',
    'fishing.html',
    'settings.html',
    'status.html'
]

new_logo_block = '''    <!-- Logo section -->
    <div class="flex items-center gap-3 cursor-pointer group" onclick="window.location.href='index.html'">
      <div class="w-10 h-10 md:w-11 md:h-11 flex items-center justify-center transition-transform group-hover:scale-105 shrink-0">
        <img src="logo.png" alt="ORCA Marine Logo" class="w-full h-full object-contain dark:hidden">
        <img src="logo-white.png" alt="ORCA Marine Logo" class="w-full h-full object-contain hidden dark:block">
      </div>
      <div>
        <h1 class="font-headline-md text-sm md:text-base font-bold text-ink dark:text-white leading-tight">ORCA Marine</h1>
        <p class="font-label-mono text-[9px] text-mute uppercase tracking-widest leading-none">Intelligence</p>
      </div>
    </div>'''

favicon_tags = '''<link rel="icon" type="image/png" href="favicon.png"/>
<link rel="shortcut icon" href="favicon.ico"/>
'''

for fname in html_files:
    fpath = os.path.join(frontend_dir, fname)
    if not os.path.exists(fpath):
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Update logo block
    # Match any Logo section div block
    logo_pattern = re.compile(
        r'<!-- Logo section -->\s*<div class="flex items-center gap-3 cursor-pointer".*?<\/div>\s*<\/div>',
        re.DOTALL
    )
    
    if logo_pattern.search(content):
        content = logo_pattern.sub(new_logo_block, content)
        print(f"Updated logo block in {fname}")
    else:
        print(f"WARNING: Could not find logo pattern in {fname}")

    # 2. Update favicon in <head>
    # Remove old icon links if present
    content = re.sub(r'<link rel="icon"[^>]*>\s*', '', content)
    content = re.sub(r'<link rel="shortcut icon"[^>]*>\s*', '', content)
    
    # Insert new favicon tags before </head>
    if '</head>' in content:
        content = content.replace('</head>', f'{favicon_tags}</head>')
        print(f"Updated favicon tags in {fname}")

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

print("All HTML files updated successfully!")
