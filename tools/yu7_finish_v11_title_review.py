"""Extract six decoded video frames to verify every label and its exit."""
from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,sys,json
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports/finish_v11';D=R/'renders/YU7_TunnelFlow/FinishShowcase_v11';name=sys.argv[1]
out=O/(name+'_TitleReview');out.mkdir(exist_ok=True)
ff=R/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
frames=[12,42,72,102,138,180];select='+'.join(f'eq(n,{f})' for f in frames)
p=subprocess.run([str(ff),'-hide_banner','-loglevel','error','-nostdin','-n','-i',str(D/(name+'_Labeled_18s.mp4')),'-vf',"select='"+select+"'",'-vsync','vfr',str(out/'decoded_%02d.png')],capture_output=True,text=True);assert p.returncode==0,p.stderr
sheet=Image.new('RGB',(1920,1770),(16,18,21));draw=ImageDraw.Draw(sheet)
for j,f in enumerate(frames):
    with Image.open(out/f'decoded_{j+1:02d}.png') as src:im=src.convert('RGB').resize((960,540))
    x=j%2*960;y=j//2*590;sheet.paste(im,(x,y+50));draw.text((x+24,y+18),f'Decoded labeled video / frame {f} / {f/24:.2f}s',fill='white')
target=out/'labels_and_exit.jpg';sheet.save(target,quality=96);print(target)
