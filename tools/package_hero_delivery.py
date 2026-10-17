"""Validate rendered frames and encode the delivery; never modifies rendered pixels."""
import json,hashlib,shutil,subprocess,re
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'art/YU7_UNREAL/reports/hero'
DEL=ROOT/'renders/YU7_MineralHero'
FF=ROOT/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
frames=DEL/'frames';still=DEL/'still'
for name in ['YU7_MineralTeal_4K','YU7_MineralTeal_Motion_4K']:
    state=json.loads((OUT/(name+'_status.json')).read_text(encoding='utf-8'))
    assert state['status']=='finished' and state['success'] and not state['errors'],state
paths=sorted(frames.glob('YU7_MineralTeal_Motion_4K_*.png'))
assert [p.name for p in paths]==[f'YU7_MineralTeal_Motion_4K_{i:04d}.png' for i in range(120)]
stats=[];previous=None
for i,p in enumerate(paths):
    with Image.open(p) as im:
        assert im.size==(3840,2160),(p,im.size);im.load()
        a=np.asarray(im.convert('RGB').resize((480,270)),dtype=np.float32)/255.
    luma=a@np.array([.2126,.7152,.0722],dtype=np.float32)
    stats.append({'frame':i,'mean_luma':float(luma.mean()),'background_luma':float(luma[:35,150:330].mean()),'mean_abs_difference':float(np.abs(a-previous).mean()) if previous is not None else 0.})
    previous=a
source=still/'YU7_MineralTeal_4K_0000.png'
with Image.open(source) as im:
    assert im.size==(3840,2160);im.verify()
for ext in ['png','exr']:
    src=still/f'YU7_MineralTeal_4K_0000.{ext}';assert src.exists()
    dest=DEL/f'YU7_MineralTeal_4K.{ext}'
    if dest.exists():assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(dest.read_bytes()).digest()
    else:shutil.copy2(src,dest)
credits=(ROOT/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
shutil.copy2(ROOT/'CREDITS.txt',DEL/'CREDITS.txt')
video=DEL/'YU7_MineralTeal_5s_4K.mp4'
assert not video.exists(),'Existing MP4 is preserved; validate it separately or choose a new output name'
cmd=[str(FF),'-hide_banner','-nostdin','-n','-framerate','24','-start_number','0','-i',str(frames/'YU7_MineralTeal_Motion_4K_%04d.png'),'-frames:v','120','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','iec61966-2-1','-colorspace','bt709','-movflags','+faststart','-metadata','title=Xiaomi YU7 | Mineral Teal | 5-second camera test','-metadata','comment='+credits,str(video)]
# Explicit H.264 VUI metadata: encoder flags alone left primaries/transfer unknown.
cmd[-1:-1]=['-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=13:matrix_coefficients=1:video_full_range_flag=0']
encoded=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
(OUT/'encode.log').write_text(encoded.stdout+'\n'+encoded.stderr,encoding='utf-8');assert encoded.returncode==0,encoded.stderr
decoded=subprocess.run([str(FF),'-hide_banner','-nostdin','-v','error','-progress','pipe:1','-i',str(video),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
(OUT/'decode.log').write_text(decoded.stdout+'\n'+decoded.stderr,encoding='utf-8')
counts=re.findall(r'^frame=(\d+)',decoded.stdout,re.M);times=re.findall(r'^out_time_us=(\d+)',decoded.stdout,re.M)
assert decoded.returncode==0 and counts and int(counts[-1])==120,(decoded.returncode,decoded.stdout,decoded.stderr)
assert times and abs(int(times[-1])/1e6-5.)<.05,times
protected=json.loads((OUT/'protected_before.json').read_text(encoding='utf-8'))
changed=[name for name,sha in protected.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha]
assert not changed,changed
deliverables={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [DEL/'YU7_MineralTeal_4K.png',DEL/'YU7_MineralTeal_4K.exr',video,DEL/'CREDITS.txt']}
result={'resolution':[3840,2160],'fps':24,'frames':120,'duration_seconds':5.,'all_png_frames_decoded':True,'mp4_full_decode':True,'protected_files_unchanged':len(protected),'changed_protected_files':changed,'deliverables':deliverables,'frame_statistics':stats,'note':'Frame statistics detect gross discontinuities; visual review is recorded separately in DEV_HISTORY.md. EXR uses the MRQ default tone curve, not raw scene-linear grading output.'}
(OUT/'delivery_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='frame_statistics'},indent=2))
