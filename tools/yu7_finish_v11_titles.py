"""Optional editorial labels, encoded from native frames (clean master retained)."""
from pathlib import Path
import sys,subprocess,json,re,hashlib
R=Path(__file__).resolve().parents[1];D=R/'renders/YU7_TunnelFlow/FinishShowcase_v11';O=R/'art/YU7_TUNNEL_FLOW/reports/finish_v11'
name=sys.argv[1];state=json.loads((O/(name+'_status.json')).read_text());assert state['success'] and not state['errors']
w=state['request']['width'];h=state['request']['height'];ff=R/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
ass=O/'finish_labels.ass'
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
labels=[('灰蓝 · 亮面车衣','GREY BLUE / GLOSS WRAP',0.,1.14),('冰蓝 · 金属漆','ICE BLUE / METALLIC PAINT',1.25,2.39),('月白 · 珠光漆','OPAL WHITE / PEARLESCENT PAINT',2.5,3.64),('石墨 · 哑光车衣','GRAPHITE / MATTE WRAP',3.75,4.89),('灰色 · 陶瓷镀膜','PORCELAIN GREY / CERAMIC GLOSS',5.,6.39)]
def ts(t):return f'0:00:{t:05.2f}'
text=header
for i,(cn,en,a,b) in enumerate(labels,1):
    text+=f'Dialogue: 0,{ts(a)},{ts(b)},CN,,0,0,0,,{{\\pos(144,1870)\\fad(100,90)}}{i:02d}  /  {cn}\n'
    text+=f'Dialogue: 0,{ts(a)},{ts(b)},EN,,0,0,0,,{{\\pos(146,1945)\\fad(100,90)}}{en}\n'
ass.write_text(text,encoding='utf-8-sig')
out=D/(name+'_Labeled_18s.mp4');assert not out.exists()
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
vf='subtitles=art/YU7_TUNNEL_FLOW/reports/finish_v11/finish_labels.ass,scale=in_range=full:out_range=tv:out_color_matrix=bt709'
cmd=[str(ff),'-hide_banner','-nostdin','-n','-framerate','24','-start_number','0','-i',str(D/name/(name+'_%04d.png')),'-frames:v','432','-vf',vf,'-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','iec61966-2-1','-colorspace','bt709','-movflags','+faststart','-metadata','title=YU7 | Material in Motion | 18 seconds','-metadata','comment='+credits,'-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=13:matrix_coefficients=1:video_full_range_flag=0',str(out)]
p=subprocess.run(cmd,cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace');(O/(name+'_titles_encode.log')).write_text(p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(ff),'-hide_banner','-nostdin','-v','error','-progress','pipe:1','-i',str(out),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace');(O/(name+'_titles_decode.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
counts=re.findall(r'^frame=(\d+)',p.stdout,re.M);times=re.findall(r'^out_time_us=(\d+)',p.stdout,re.M);assert p.returncode==0 and int(counts[-1])==432 and abs(int(times[-1])/1e6-18)<.05
report={'video':out.relative_to(R).as_posix(),'resolution':[w,h],'frames':432,'fps':24,'duration_seconds':18,'complete_decode':True,'source':'Native UE PNG sequence with editorial finish labels only','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'labels':labels}
(O/(name+'_titles_validation.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(report,ensure_ascii=True))
