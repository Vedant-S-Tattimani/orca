import sys

with open(r'd:\orca\orca-frontend\dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '} else {' in line or 'else {' in line or '}else {' in line:
        print(f"Line {i+1}: {line.strip()}")
