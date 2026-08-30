import os
import re

directory = r'd:\orca\orca-frontend'
html_files = [f for f in os.listdir(directory) if f.endswith('.html')]

# Clean up all theme toggle remnants
pattern = re.compile(r'(?s)\s*const handleThemeToggle = \(\) => \{.*?(?:toggleBtnNav\.addEventListener\(\'click\', handleThemeToggle\);\s*\}\s*|\s*\}\s*)', re.IGNORECASE)
pattern2 = re.compile(r'(?s)\s*const toggleBtnNav = document\.getElementById\(\'theme-toggle-btn-nav\'\);\s*if \(toggleBtnNav\) \{\s*toggleBtnNav\.addEventListener\(\'click\', handleThemeToggle\);\s*\}')
pattern3 = re.compile(r'(?s)\s*const toggleBtn = document\.getElementById\(\'theme-toggle-btn\'\);\s*if \(toggleBtn\) \{\s*toggleBtn\.addEventListener\(\'click\', handleThemeToggle\);\s*\}')
pattern4 = re.compile(r'(?s)\s*const toggleBtnNav = document\.getElementById\(\'theme-toggle-btn-nav\'\);\s*if \(toggleBtnNav\) toggleBtnNav\.addEventListener\(\'click\', handleThemeToggle\);')

for filename in html_files:
    filepath = os.path.join(directory, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig = content
    content = pattern.sub('', content)
    content = pattern2.sub('', content)
    content = pattern3.sub('', content)
    content = pattern4.sub('', content)
    
    if orig != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filename}")
