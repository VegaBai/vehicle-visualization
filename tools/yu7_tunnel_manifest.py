from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];D=R/'renders/YU7_TunnelFlow';O=R/'art/YU7_TUNNEL_FLOW/reports'
v=json.loads((O/'Final_v06_4K_validation.json').read_text());assert v['mp4_complete_decode']
for f,label in [(24,'01_CleanPaint'),(96,'02_SurfaceFlow'),(163,'03_QuadRelay'),(228,'04_FullBodyAfterglow'),(276,'05_FadeOut')]:
    src=D/'Final_v06_4K'/f'Final_v06_4K_{f:04d}.png';dest=D/(label+'_4K.png')
    if dest.exists():assert hashlib.sha256(dest.read_bytes()).digest()==hashlib.sha256(src.read_bytes()).digest()
    else:shutil.copy2(src,dest)
for folder in [R/'art/YU7_TUNNEL_FLOW',D]:assert (folder/'CREDITS.txt').read_bytes()==(R/'CREDITS.txt').read_bytes()
files=[]
for folder in [R/'VehicleStudio/Content/YU7/TunnelFlow',R/'art/YU7_TUNNEL_FLOW/prepared']:
    files.extend(p for p in folder.rglob('*') if p.is_file())
files.extend(p for p in D.iterdir() if p.is_file() and (p.name in ['Final_v06_4K_12s.mp4','YU7_TunnelFlow_12s_1080p.mp4','CREDITS.txt'] or p.name.startswith(('01_','02_','03_','04_','05_'))))
manifest={'assets':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)],'native_sequence':'/Game/YU7/TunnelFlow/Sequences/LS_YU7_TunnelFlow_12s','map':'/Game/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow','frames':288,'fps':24,'credits_exact':True}
(O/'output_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps({'assets':len(files),'report':str(O/'output_manifest.json')}))
