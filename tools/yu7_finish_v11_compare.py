"""Review derivative only: six actual native finish frames in a single sheet."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];D=R/'renders/YU7_TunnelFlow/FinishShowcase_v11';name=sys.argv[1]
frames=[12,42,72,102,138,180]
labels=['01  灰蓝亮面车衣','02  冰蓝金属漆','03  月白珠光漆','04  石墨哑光车衣','05  灰色陶瓷镀膜','06  回归矿物青']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
out=Image.new('RGB',(1920,1770),(16,18,21));draw=ImageDraw.Draw(out)
for j,(f,label) in enumerate(zip(frames,labels)):
    with Image.open(D/name/f'{name}_{f:04d}.png') as src:im=src.convert('RGB').resize((960,540))
    x=j%2*960;y=j//2*590;out.paste(im,(x,y+50));draw.text((x+24,y+9),label,font=font,fill=(225,234,239))
p=D/(name+'_FinishComparison.jpg');out.save(p,quality=96)
print(p)
