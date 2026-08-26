import os
import re
import numpy as np
from PIL import Image
import vtracer

input_img_path = r'C:\Users\Abhishek\.gemini\antigravity\brain\f62ab47f-cea4-4b05-a2b0-0f2f6b3dc423\media__1787739429034.jpg'
frontend_dir = r'c:\Users\Abhishek\OneDrive\Desktop\orca clone\orca\orca-frontend'

img = Image.open(input_img_path).convert('RGBA')
arr = np.array(img)

# Threshold for black shapes
rgb_sum = arr[:, :, 0].astype(int) + arr[:, :, 1].astype(int) + arr[:, :, 2].astype(int)
is_dark = rgb_sum < 320

# Create transparent RGBA image
trans_arr = np.zeros((img.height, img.width, 4), dtype=np.uint8)

# Smooth alpha transition
for y in range(img.height):
    for x in range(img.width):
        v = rgb_sum[y, x] / 3.0
        if v < 200:
            alpha = int(255 * (1.0 - max(0.0, (v - 20.0) / 180.0)))
            trans_arr[y, x] = [15, 23, 42, alpha] # sleek dark slate/black #0f172a

png_transparent = Image.fromarray(trans_arr)

# Find bounding box
bbox = png_transparent.getbbox()
if bbox:
    margin = 12
    crop_box = (
        max(0, bbox[0] - margin),
        max(0, bbox[1] - margin),
        min(img.width, bbox[2] + margin),
        min(img.height, bbox[3] + margin)
    )
    cropped = png_transparent.crop(crop_box)
    
    # Make square with transparent padding
    w, h = cropped.size
    max_dim = max(w, h)
    square_img = Image.new('RGBA', (max_dim, max_dim), (0, 0, 0, 0))
    offset_x = (max_dim - w) // 2
    offset_y = (max_dim - h) // 2
    square_img.paste(cropped, (offset_x, offset_y))
    
    # Resize to standard high-res 512x512 square
    png_transparent = square_img.resize((512, 512), Image.Resampling.LANCZOS)

# Save logo.png
logo_png_path = os.path.join(frontend_dir, 'logo.png')
png_transparent.save(logo_png_path, 'PNG')

# Save inverted white version (logo-white.png) for dark mode
white_trans_arr = np.array(png_transparent)
white_trans_arr[:, :, 0] = 255
white_trans_arr[:, :, 1] = 255
white_trans_arr[:, :, 2] = 255
png_white_transparent = Image.fromarray(white_trans_arr)

logo_white_png_path = os.path.join(frontend_dir, 'logo-white.png')
png_white_transparent.save(logo_white_png_path, 'PNG')

# Favicon PNG (64x64 and 32x32) & ICO
favicon_64 = png_transparent.resize((64, 64), Image.Resampling.LANCZOS)
favicon_png_path = os.path.join(frontend_dir, 'favicon.png')
favicon_64.save(favicon_png_path, 'PNG')

# For favicon.ico, we create a high visibility favicon (white in dark/light or circle badge)
favicon_32 = png_transparent.resize((32, 32), Image.Resampling.LANCZOS)
favicon_ico_path = os.path.join(frontend_dir, 'favicon.ico')
favicon_32.save(favicon_ico_path, format='ICO')

# Save logo.svg with crisp vector tracing
bw_img = Image.new('L', (512, 512), 255)
bw_arr = np.array(bw_img)
bw_arr[np.array(png_transparent)[:, :, 3] > 100] = 0
bw_clean = Image.fromarray(bw_arr)

temp_bw_path = os.path.join(frontend_dir, 'temp_bw.png')
bw_clean.save(temp_bw_path)

raw_svg_path = os.path.join(frontend_dir, 'raw_logo.svg')
vtracer.convert_image_to_svg_py(temp_bw_path, raw_svg_path)

with open(raw_svg_path, 'r', encoding='utf-8') as f:
    svg_content = f.read()

cleaned_paths = []
path_matches = re.findall(r'<path[^>]+>', svg_content)
for i, p in enumerate(path_matches):
    p_lower = p.lower()
    if 'fill="#f' in p_lower or 'fill="#e' in p_lower or 'fill="#fff' in p_lower or i == 0:
        continue
    p_curr = re.sub(r'fill="[^"]+"', 'fill="currentColor"', p)
    cleaned_paths.append(p_curr)

final_svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%" class="orca-logo-svg">
  <g class="orca-logo-group">
    {"".join(cleaned_paths)}
  </g>
</svg>'''

logo_svg_path = os.path.join(frontend_dir, 'logo.svg')
with open(logo_svg_path, 'w', encoding='utf-8') as f:
    f.write(final_svg_content)

favicon_svg_path = os.path.join(frontend_dir, 'favicon.svg')
with open(favicon_svg_path, 'w', encoding='utf-8') as f:
    f.write(final_svg_content)

if os.path.exists(temp_bw_path):
    os.remove(temp_bw_path)
if os.path.exists(raw_svg_path):
    os.remove(raw_svg_path)

print("All logo and favicon assets updated to perfectly padded 512x512 square assets!")
