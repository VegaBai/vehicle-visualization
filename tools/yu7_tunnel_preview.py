"""Make a lightweight 1080p viewing copy from the verified native 4K movie."""
from pathlib import Path
import subprocess,json,re,hashlib
R=Path(__file__).resolve().parents[1];D=R/'renders/YU7_TunnelFlow';O=R/'art/YU7_TUNNEL_FLOW/reports';F=R/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
master=D/'Final_v06_4K_12s.mp4';dest=D/'YU7_TunnelFlow_12s_1080p.mp4'
assert json.loads((O/'Final_v06_4K_validation.json').read_text())['mp4_complete_decode'];assert not dest.exists()
credit=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
cmd=[str(F),'-hide_banner','-nostdin','-n','-i',str(master),'-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','iec61966-2-1','-colorspace','bt709','-movflags','+faststart','-metadata','title=Xiaomi YU7 | Flow into Form','-metadata','comment='+credit,'-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=13:matrix_coefficients=1:video_full_range_flag=0',str(dest)]
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');(O/'preview_encode.log').write_text(p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(F),'-hide_banner','-nostdin','-v','error','-progress','pipe:1','-i',str(dest),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
counts=re.findall(r'^frame=(\d+)',p.stdout,re.M);times=re.findall(r'^out_time_us=(\d+)',p.stdout,re.M);assert p.returncode==0 and int(counts[-1])==288 and abs(int(times[-1])/1e6-12)<.05
result={'path':str(dest),'resolution':[1920,1080],'frames':288,'fps':24,'duration':12,'complete_decode':True,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'operation':'Lanczos downscale of native UE master, H.264 viewing copy; no AI or compositing.'}
(O/'preview_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
