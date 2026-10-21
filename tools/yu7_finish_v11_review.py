"""Every-frame contact sheets and a labeled finish comparison for visual review."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];D=R/'renders/YU7_TunnelFlow/FinishShowcase_v11';name=sys.argv[1]
dest=D/(name+'_Review');dest.mkdir(exist_ok=True)
files=sorted((D/name).glob(name+'_*.png'));partial='--partial' in sys.argv
limit=(max(0,len(files)-1)//24)*24 if partial else 432
if not partial:assert len(files)==432
created=[]
for start in range(0,limit,24):
    target=dest/f'frames_{start:03d}_{start+23:03d}.jpg'
    if target.exists():continue
    out=Image.new('RGB',(1920,800),(16,18,21));draw=ImageDraw.Draw(out)
    for j in range(24):
        with Image.open(files[start+j]) as src:im=src.convert('RGB').resize((320,180))
        x=j%6*320;y=j//6*200;out.paste(im,(x,y+20));draw.text((x+8,y+4),f'{start+j:03d}  {(start+j)/24:.3f}s',fill='white')
    out.save(target,quality=94);created.append(target.name)
print(json.dumps({'present':len(files),'covered':limit,'created':created,'directory':str(dest)}))
