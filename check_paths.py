import re

with open('orca-frontend/logo.svg', 'r', encoding='utf-8') as f:
    svg = f.read()

paths = re.findall(r'<path[^>]+>', svg)
print("Total paths:", len(paths))
for i, p in enumerate(paths):
    d = re.search(r'd="([^"]+)"', p)
    d_val = d.group(1) if d else ""
    print(f"Path {i}: starts with '{d_val[:40]}...', total length {len(d_val)}")
