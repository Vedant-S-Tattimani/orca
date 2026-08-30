import re

with open(r'd:\orca\orca-frontend\dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'(?s)<script>(.*?)</script>', content)
for i, s in enumerate(scripts):
    with open(fr'd:\orca\orca-frontend\script_{i}.js', 'w', encoding='utf-8') as sf:
        sf.write(s)
