"""Extract actual encoded label samples for visual review, without editing delivery."""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
O = R / 'art/YU7_TUNNEL_FLOW/reports/itasha_v12'
D = R / 'renders/YU7_TunnelFlow/ItashaShowcase_v12'
ff = R / 'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
sheet = Image.new('RGB', (1920, 1152), (18, 18, 18))
for i, t in enumerate([0.5, 1.7, 3, 4.2, 5.5, 7, 9, 11, 12.5]):
    out = O / f'final_label_{i}.png'
    subprocess.run([str(ff), '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
                    '-ss', str(t), '-i', str(D / 'Final_r03_4K_Labeled_24s.mp4'),
                    '-frames:v', '1', str(out)], check=True)
    with Image.open(out) as im:
        thumb = im.convert('RGB').resize((640, 360))
    x, y = (i % 3) * 640, (i // 3) * 384
    sheet.paste(thumb, (x, y))
    ImageDraw.Draw(sheet).text((x+8, y+363), f'{t}s', fill='white')
sheet.save(O / 'final_label_review.jpg', quality=94)
print('Extracted nine samples from encoded 4K labeled MP4')
