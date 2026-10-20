"""Package verified roof revision media, keeping every prior deliverable unchanged."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports';D=R/'renders/YU7_TunnelFlow'
v=json.loads((O/'Previs_v07_1080p_validation.json').read_text());assert v['mp4_complete_decode'] and v['frames']==288
s=json.loads((O/'Roof_Keyframes_v07_4K_status.json').read_text());assert s['success'] and not s['errors']
stills=[]
for frame,name in [(96,'RoofAirflow_v07_4K.png'),(228,'RoofFullBody_v07_4K.png')]:
    src=D/'Roof_Keyframes_v07_4K'/f'Roof_Keyframes_v07_4K_{frame:04d}.png';dest=D/name
    with Image.open(src) as im:im.load();assert im.size==(3840,2160)
    assert not dest.exists();shutil.copy2(src,dest);stills.append(dest)
old=json.loads((O/'roof_protected_before.json').read_text());changed=[p['path'] for p in old if hashlib.sha256((R/p['path']).read_bytes()).hexdigest()!=p['sha256']];assert not changed,changed
assets=[R/'VehicleStudio/Content/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow.umap',R/'VehicleStudio/Content/YU7/TunnelFlow/Blueprints/BP_TunnelRoofAirflow_v01.uasset',R/'VehicleStudio/Content/YU7/TunnelFlow/Materials/M_TunnelRoofAirflow_v01.uasset']
assets.extend(p for p in (R/'VehicleStudio/Content/YU7/TunnelFlow/Meshes/RoofAirflow_v01').rglob('*') if p.is_file())
assets.extend([R/'art/YU7_TUNNEL_FLOW/prepared/YU7_RoofAirflow_v01.blend',R/'art/YU7_TUNNEL_FLOW/prepared/YU7_RoofAirflow_v01.fbx',D/'Previs_v07_1080p_12s.mp4',D/'CREDITS.txt']+stills)
assert (D/'CREDITS.txt').read_bytes()==(R/'CREDITS.txt').read_bytes()
result={'assets':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in assets],'full_video':'Previs_v07_1080p_12s.mp4','full_video_resolution':[1920,1080],'frames':288,'fps':24,'native_4K_stills':2,'v06_protected_unchanged':len(old),'v07_full_4K_movie':'Not rendered; prior Final_v06_4K_12s.mp4 is the previous version','audio':'Silent','credits_exact':True}
(O/'roof_output_manifest_v07.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='assets'},indent=2))
