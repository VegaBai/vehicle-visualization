"""Contact sheets for every native frame, plus denser roof/detail strips."""
from PIL import Image,ImageDraw
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];D=R/'renders/YU7_TunnelFlow/ArtDirection_v09';name=sys.argv[1]
dest=D/(name+'_Review');dest.mkdir(exist_ok=True)
files=sorted((D/name).glob(name+'_*.png'))
partial='--partial' in sys.argv
if not partial:assert len(files)==288
limit=((max(0,len(files)-1)//24)*24) if partial else 288
created=[]
for start in range(0,limit,24):
    target=dest/f'frames_{start:03d}_{start+23:03d}.jpg'
    if target.exists():continue
    out=Image.new('RGB',(1920,800),(18,18,18));draw=ImageDraw.Draw(out)
    for j in range(24):
        im=Image.open(files[start+j]).convert('RGB').resize((320,180));x=(j%6)*320;y=(j//6)*200
        out.paste(im,(x,y+20));draw.text((x+8,y+4),f'{start+j:03d}  {(start+j)/24:.3f}s',fill='white')
    out.save(target,quality=94);created.append(target.name)
# Roof-only strips at native 1080p-equivalent detail for visibility/phase review.
for start in [84,108,156,204,216,252,264]:
    target=dest/f'roof_{start:03d}.jpg'
    if start+24>limit or target.exists():continue
    out=Image.new('RGB',(1920,600),(18,18,18));draw=ImageDraw.Draw(out)
    for j,f in enumerate(range(start,start+24,4)):
        with Image.open(files[f]) as src:
            w,h=src.size;im=src.crop((int(w*.15),int(h*.20),int(w*.9),int(h*.56))).resize((640,276))
        x=(j%3)*640;y=(j//3)*300;out.paste(im,(x,y+24));draw.text((x+8,y+5),f'frame {f}',fill='white')
    out.save(target,quality=95);created.append(target.name)
print(json.dumps({'native_frames_present':len(files),'covered_frames':limit,'partial':partial,'created':created,'directory':str(dest),'note':'Review derivatives only; delivered images are unmodified native frames.'}))
