"""Create review sheets from completed groups while MRQ continues."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12'
name=sys.argv[1];state=json.loads((O/(name+'_status.json')).read_text());source=R/'renders/YU7_TunnelFlow/ItashaShowcase_v12/frames'/name
files=sorted(source.glob('*.png'));count=len(files) if state['status']=='finished' else max(0,len(files)-1)
out=O/(name+'_review');out.mkdir(exist_ok=True);created=[]
for group in range(count//24):
    dest=out/f'sheet_{group:02d}.jpg'
    if dest.exists():continue
    sheet=Image.new('RGB',(1920,816),(18,18,18));draw=ImageDraw.Draw(sheet)
    for j,p in enumerate(files[group*24:group*24+24]):
        with Image.open(p) as im:im.load();thumb=im.convert('RGB').resize((320,180))
        x=j%6*320;y=j//6*204;sheet.paste(thumb,(x,y));draw.text((x+8,y+183),f'{group*24+j:04d} / {(group*24+j)/24:.2f}s',fill=(230,230,230))
    sheet.save(dest,quality=90);created.append(group)
print(json.dumps({'status':state['status'],'frames':len(files),'new_sheets':created,'complete_sheets':count//24,'errors':state['errors']}))
