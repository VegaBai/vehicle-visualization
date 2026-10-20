"""Preserve v07 deliverables and record the actual native v08 media and assets."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports';D=R/'renders/YU7_TunnelFlow'
v=json.loads((O/'Previs_v08_1080p_validation.json').read_text());assert v['mp4_complete_decode'] and v['frames']==288
s=json.loads((O/'Pulse_Keyframes_v08_4K_status.json').read_text());assert s['success'] and not s['errors']
stills=[]
for frame,name in [(96,'RoofPulse_v08_4K.png'),(228,'RoofPulseFullBody_v08_4K.png')]:
    src=D/'Pulse_Keyframes_v08_4K'/f'Pulse_Keyframes_v08_4K_{frame:04d}.png';dest=D/name
    with Image.open(src) as im:im.load();assert im.size==(3840,2160)
    if dest.exists():assert dest.read_bytes()==src.read_bytes()
    else:shutil.copy2(src,dest)
    stills.append(dest)
old=json.loads((O/'pulse_protected_before.json').read_text());changed=[p['path'] for p in old if hashlib.sha256((R/p['path']).read_bytes()).hexdigest()!=p['sha256']];assert not changed,changed
assets=[R/'VehicleStudio/Content/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow.umap',R/'VehicleStudio/Content/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow_BeforePulse_v07.umap',R/'VehicleStudio/Content/YU7/TunnelFlow/Materials/M_TunnelRoofAirflow_Pulse_v02.uasset']
assets.extend(sorted((R/'VehicleStudio/Content/YU7/TunnelFlow/RenderPresets').glob('*v08*.uasset')))
assets.extend([D/'Previs_v08_1080p_12s.mp4',D/'CREDITS.txt']+stills)
assert (D/'CREDITS.txt').read_bytes()==(R/'CREDITS.txt').read_bytes()
result={'assets':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in assets],'full_video':'Previs_v08_1080p_12s.mp4','full_video_resolution':[1920,1080],'frames':288,'fps':24,'native_4K_stills':2,'v07_protected_unchanged':len(old),'v08_full_4K_movie':'Not rendered; Final_v06_4K_12s.mp4 remains the earlier version','audio':'Silent','credits_exact':True,'motion':'MPC ShotTime brightness packets and native WPO vertical/lateral waves; illustrative, not CFD'}
(O/'pulse_output_manifest_v08.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='assets'},indent=2))
