"""Snapshot every existing UE asset, authored source and curated historical medium."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09'
O.mkdir(parents=True,exist_ok=True)
dest=O/'protected_before.json';assert not dest.exists()
files=set((R/'VehicleStudio/Content').rglob('*.uasset'))|set((R/'VehicleStudio/Content').rglob('*.umap'))
for directory in ['art/FINAL_MODEL','art/YU7_UNREAL','art/YU7_WIREFRAME','art/YU7_QUAD_BODY','art/YU7_TUNNEL_FLOW/prepared']:
    files.update(p for p in (R/directory).rglob('*') if p.is_file() and 'reports' not in p.parts and p.suffix not in ['.blend1','.blend2'])
files.update(p for p in (R/'renders/YU7_TunnelFlow').iterdir() if p.is_file())
for name in ['protected_before.json','pulse_protected_before.json','pulse_output_manifest_v08.json']:
    old=json.loads((R/'art/YU7_TUNNEL_FLOW/reports'/name).read_text())
    if isinstance(old,dict):old=old['assets']
    for row in old:
        p=R/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],str(p)
        files.add(p)
rows=[{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
dest.write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps({'protected':len(rows),'old_420_71_manifest_checks':True}))
