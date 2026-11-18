"""Validate all native frames; encode clean/labeled video and review sheets."""
from pathlib import Path
import json,sys,subprocess,hashlib,re,shutil
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12';D=R/'renders/YU7_TunnelFlow/ItashaShowcase_v12'
name=sys.argv[1];state=json.loads((O/(name+'_status.json')).read_text());assert state['status']=='finished' and state['success'] and not state['errors']
w,h=state['request']['width'],state['request']['height'];frames=sorted((D/'frames'/name).glob('*.png'));assert len(frames)==576
review=O/(name+'_review');review.mkdir(exist_ok=True);stats=[];prev=None;sheet=None
for i,p in enumerate(frames):
    assert p.name==f'{name}_{i:04d}.png'
    with Image.open(p) as im:
        im.load();assert im.size==(w,h);thumb=im.convert('RGB').resize((320,180));a=np.asarray(thumb,dtype=float)/255
    stats.append({'frame':i,'mean':float(a.mean()),'difference':float(np.abs(a-prev).mean()) if prev is not None else 0});prev=a
    if i%24==0:sheet=Image.new('RGB',(1920,816),(18,18,18))
    x=(i%6)*320;y=((i%24)//6)*204;sheet.paste(thumb,(x,y));ImageDraw.Draw(sheet).text((x+8,y+183),f'{i:04d} / {i/24:.2f}s',fill=(230,230,230))
    if i%24==23:sheet.save(review/f'sheet_{i//24:02d}.jpg',quality=90)
assert min(s['mean'] for s in stats)>.015
(O/(name+'_frame_stats.json')).write_text(json.dumps(stats,indent=2))
ff=R/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe';credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
labels=[('灰蓝 · 亮面车衣','GREY BLUE / GLOSS WRAP',0,1.0),('冰蓝 · 金属漆','ICE BLUE / METALLIC PAINT',1.25,2.25),('月白 · 珠光漆','OPAL WHITE / PEARLESCENT PAINT',2.5,3.5),('石墨 · 哑光车衣','GRAPHITE / MATTE WRAP',3.75,4.75),('灰色 · 陶瓷镀膜','PORCELAIN GREY / CERAMIC GLOSS',5,6),('炎柱 · 珠光白','RENGOKU / PEARL WHITE',6.25,8),('善逸 · 石墨灰','ZENITSU / GRAPHITE',8.25,10),('义勇 · 矿物青','GIYU / MINERAL TEAL',10.25,12)]
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 3840
PlayResY: 2160
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CN,Microsoft YaHei,48,&H00F0EEE8,&H000000FF,&H70000000,&H70000000,0,0,0,0,100,100,2,0,1,1,1,7,144,144,144,1
Style: EN,Arial,25,&H00B8B1A7,&H000000FF,&H70000000,&H70000000,0,0,0,0,100,100,4,0,1,1,1,7,144,144,144,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for i,(cn,en,a,b) in enumerate(labels,1):
    header+=f'Dialogue: 0,0:00:{a:05.2f},0:00:{b:05.2f},CN,,0,0,0,,{{\\pos(144,1870)\\fad(80,80)}}{i:02d}  /  {cn}\n'
    header+=f'Dialogue: 0,0:00:{a:05.2f},0:00:{b:05.2f},EN,,0,0,0,,{{\\pos(146,1945)\\fad(80,80)}}{en}\n'
(O/'labels.ass').write_text(header,encoding='utf-8-sig')
outputs=[]
for labeled in [False,True]:
    out=D/(name+('_Labeled' if labeled else '')+'_24s.mp4');assert not out.exists() or '--resume' in sys.argv,out
    vf=('subtitles=art/YU7_TUNNEL_FLOW/reports/itasha_v12/labels.ass,' if labeled else '')+'scale=in_range=full:out_range=tv:out_color_matrix=bt709'
    cmd=[str(ff),'-hide_banner','-nostdin','-n','-framerate','24','-start_number','0','-i',str(D/'frames'/name/(name+'_%04d.png')),'-frames:v','576','-vf',vf,'-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','iec61966-2-1','-colorspace','bt709','-movflags','+faststart','-metadata','title=YU7 | Paint, Itasha and Flow | 24 seconds','-metadata','comment='+credits,str(out)]
    if not out.exists():
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace');(O/(out.stem+'_encode.log')).write_text(result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
    result=subprocess.run([str(ff),'-hide_banner','-nostdin','-v','error','-progress','pipe:1','-i',str(out),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
    (O/(out.stem+'_decode.log')).write_text(result.stdout+'\n'+result.stderr)
    counts=re.findall(r'^frame=(\d+)',result.stdout,re.M);times=re.findall(r'^out_time_us=(\d+)',result.stdout,re.M)
    assert result.returncode==0 and not result.stderr.strip() and int(counts[-1])==576 and abs(int(times[-1])/1e6-24)<.05
    outputs.append({'path':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'complete_decode':True})
shutil.copy2(R/'CREDITS.txt',D/'CREDITS.txt');shutil.copy2(R/'renders/YU7_Itasha_v01/ART_SOURCES.txt',D/'ART_SOURCES.txt')
report={'outputs':outputs,'frames':576,'fps':24,'duration_seconds':24,'resolution':[w,h],'all_native_png_decoded':True,'visual_review':'pending','audio':'silent','labels':labels}
(O/(name+'_validation.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=True))
