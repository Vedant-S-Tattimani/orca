import os

src_dir = r'd:\orca'
dest_dir = r'd:\orca\orca-backend\tests'

files_to_move = [
    ('test_boundary.py', 'test_boundary.py'),
    ('test_sos.py', 'test_sos.py'),
    ('test_last_known.py', 'test_last_known.py'),
    ('test_trips.py', 'test_trips.py'),
    ('test_emergency_route.py', 'test_emergency_route.py'),
    (r'orca-backend\test_weather_agent.py', 'test_weather_agent2.py') # renaming to avoid conflict if it exists, or just test_weather_agent.py
]

for src, dest in files_to_move:
    src_path = os.path.join(src_dir, src)
    dest_path = os.path.join(dest_dir, dest)
    if not os.path.exists(src_path):
        print(f'Skipping {src_path}')
        continue
        
    with open(src_path, 'r') as f:
        content = f.read()
    
    # Remove if __name__ == '__main__': block
    lines = content.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if line.startswith('if __name__ =='):
            skip = True
        if skip and (not line.startswith(' ') and not line.startswith('\t') and line.strip() != '' and not line.startswith('if __name__')):
            skip = False # we shouldn't really hit this for standard main blocks
        if not skip:
            new_lines.append(line)
    
    content = '\n'.join(new_lines).strip()
    
    # Add pytest imports and mark if not present
    if 'import pytest' not in content:
        content = 'import pytest\n' + content
        
    # Replace async def test with @pytest.mark.asyncio\nasync def test
    content = content.replace('async def test_', '@pytest.mark.asyncio\nasync def test_')
    content = content.replace('def test_', 'def test_') # nothing for sync

    with open(dest_path, 'w') as f:
        f.write(content)
        
    print(f'Moved and updated {src} to {dest}')
