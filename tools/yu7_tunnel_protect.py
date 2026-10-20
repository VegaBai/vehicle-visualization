from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
out=R/'art/YU7_TUNNEL_FLOW/reports/protected_before.json'
assert not out.exists()
paths=[]
for name in ['VehicleStudio/Content','art/FINAL_MODEL','art/YU7_UNREAL','art/YU7_WIREFRAME','art/YU7_QUAD_BODY']:
    for p in (R/name).rglob('*'):
        if p.is_file() and (name=='VehicleStudio/Content' or p.suffix.lower() in ['.fbx','.blend','.png','.jpg','.jpeg','.tga','.exr','.txt']):paths.append(p)
rows=[{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(paths))]
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps({'protected':len(rows),'report':str(out)}))
