import os
import re

directory = r'd:\orca\orca-frontend'
html_files = [f for f in os.listdir(directory) if f.endswith('.html')]

# The exact block that was orphaned:
#  // (?:[0-9]\. )?Theme Toggle logicelse \{
#  ...
#  \};
pattern = re.compile(
    r'(?s)\s*// (?:[0-9]\. )?Theme Toggle (?:logic)?else \{\s*document\.documentElement\.classList\.add\(\'dark\'\);\s*document\.documentElement\.classList\.remove\(\'light\'\);\s*localStorage\.setItem\(\'orca_theme\', \'dark\'\);\s*\}\s*\};\s*',
    re.IGNORECASE
)

for filename in html_files:
    filepath = os.path.join(directory, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig = content
    content = pattern.sub('\n', content)
    
    if orig != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed syntax error in {filename}")
