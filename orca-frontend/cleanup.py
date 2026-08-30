import os
import re

directory = r'd:\orca\orca-frontend'
html_files = [f for f in os.listdir(directory) if f.endswith('.html')]

# Pattern to remove mobile menu logic
mobile_pattern = re.compile(
    r'(?s)\s*// (?:Mobile )?(?:m|M)enu toggle.*?(?:const|let) menuBtn = document\.getElementById\(\'mobile-menu-btn\'\);.*?(?:}\);|})\n\s*}\s*\n', 
    re.IGNORECASE
)
mobile_pattern_2 = re.compile(
    r'(?s)\s*(?:// 1\. Initialize Nav & Mobile Menu|// 1\. Setup Mobile Menu)\s*(?:const|let) menuBtn = document\.getElementById\(\'mobile-menu-btn\'\);.*?(?:}\);|})\n\s*}\n'
)
mobile_pattern_3 = re.compile(
    r'(?s)\s*(?:const|let) menuBtn = document\.getElementById\(\'mobile-menu-btn\'\);.*?navMenu\.classList\.toggle\(\'hidden\'\);\s*(?:}\);|})\s*}\n'
)


# Pattern to remove theme toggle logic
theme_pattern_1 = re.compile(
    r'(?s)\s*// Theme Toggle.*?(?:const|let) handleThemeToggle = \(\) => \{.*?localStorage\.setItem\(\'orca_theme\', \'dark\'\);\s*\}\s*\};\s*const toggleBtnNav = document\.getElementById\(\'theme-toggle-btn-nav\'\);\s*if \(toggleBtnNav\)\s*toggleBtnNav\.addEventListener\(\'click\', handleThemeToggle\);'
)
theme_pattern_2 = re.compile(
    r'(?s)\s*// Theme Toggle.*?(?:const|let) handleThemeToggle = \(\) => \{.*?localStorage\.setItem\(\'orca_theme\', \'dark\'\);\s*\}\s*\};\s*const toggleBtnNav = document\.getElementById\(\'theme-toggle-btn-nav\'\);\s*if \(toggleBtnNav\) \{\s*toggleBtnNav\.addEventListener\(\'click\', handleThemeToggle\);\s*\}'
)
theme_pattern_3 = re.compile(
    r'(?s)\s*// Theme Toggle inside Navbar\s*const toggleBtnNav = document\.getElementById\(\'theme-toggle-btn-nav\'\);.*?localStorage\.setItem\(\'orca_theme\', \'dark\'\);\s*\}\s*\}\);\s*\}'
)

for filename in html_files:
    filepath = os.path.join(directory, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig_content = content
    content = mobile_pattern.sub('', content)
    content = mobile_pattern_2.sub('', content)
    content = mobile_pattern_3.sub('', content)
    content = theme_pattern_1.sub('', content)
    content = theme_pattern_2.sub('', content)
    content = theme_pattern_3.sub('', content)
    
    if orig_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filename}")
