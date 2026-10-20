"""Decode every native frame, encode tagged H.264, verify protected sources."""
from pathlib import Path
import json,sys,subprocess,hashlib,shutil,re
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports';D=R/'renders/YU7_TunnelFlow'
name=sys.argv[1];state=json.loads((O/(name+'_status.json')).read_text());assert state['status']=='finished' and state['success'] and not state['errors'],state
assert 'frames' not in state['request'];width=state['request'].get('width',1280);height=state['request'].get('height',720)
frames=sorted((D/name).glob(name+'_*.png'));assert len(frames)==288
statistics=[];previous=None
for i,p in enumerate(frames):
    assert p.name==f'{name}_{i:04d}.png'
    with Image.open(p) as im:
        im.load();assert im.size==(width,height)
        a=np.asarray(im.convert('RGB').resize((320,180)),dtype=np.float32)/255
    statistics.append({'frame':i,'mean':float(a.mean()),'difference':float(np.abs(a-previous).mean()) if previous is not None else 0});previous=a
flags=[s for i,s in enumerate(statistics) if i>0 and s['difference']>.055 and s['mean']<statistics[i-1]['mean']*.75]
(O/(name+'_frame_review.json')).write_text(json.dumps({'abrupt_darkening_flags':flags,'last_frame_mean':statistics[-1]['mean'],'note':'Gross discontinuity detection, not a replacement for visual inspection.'},indent=2),encoding='utf-8')
assert not flags,flags
ff=R/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe';video=D/(name+'_12s.mp4');assert not video.exists()
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip();shutil.copy2(R/'CREDITS.txt',D/'CREDITS.txt')
cmd=[str(ff),'-hide_banner','-nostdin','-n','-framerate','24','-start_number','0','-i',str(D/name/(name+'_%04d.png')),'-frames:v','288','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','iec61966-2-1','-colorspace','bt709','-movflags','+faststart','-metadata','title=Xiaomi YU7 | Flow into Form | 12 seconds','-metadata','comment='+credits,'-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=13:matrix_coefficients=1:video_full_range_flag=0',str(video)]
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');(O/(name+'_encode.log')).write_text(p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(ff),'-hide_banner','-nostdin','-v','error','-progress','pipe:1','-i',str(video),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace');(O/(name+'_decode.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
counts=re.findall(r'^frame=(\d+)',p.stdout,re.M);times=re.findall(r'^out_time_us=(\d+)',p.stdout,re.M)
assert p.returncode==0 and int(counts[-1])==288 and abs(int(times[-1])/1e6-12)<.05
protected=json.loads((O/'protected_before.json').read_text());changed=[r['path'] for r in protected if hashlib.sha256((R/r['path']).read_bytes()).hexdigest()!=r['sha256']];assert not changed,changed
result={'video':str(video),'resolution':[width,height],'fps':24,'frames':288,'duration_seconds':12,'decoded_png_frames':True,'mp4_complete_decode':True,'protected_unchanged':len(protected),'changed_protected':changed,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'statistics':statistics,'audio':'Silent visual review; proposed sound design has not been produced.'}
(O/(name+'_validation.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='statistics'},indent=2))
