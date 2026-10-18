"""Snapshot existing vehicle assets and accepted partial study without modifying them."""
import hashlib,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization')
OUT=ROOT/'art/YU7_QUAD_BODY/reports/protected_before.json'
assert not OUT.exists()
paths=[]
for folder in ['art/FINAL_MODEL','art/YU7_UNREAL','art/YU7_WIREFRAME','VehicleStudio/Content','renders/YU7_WireframeStudy']:
    paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() in {'.fbx','.blend','.png','.jpg','.jpeg','.webp','.uasset','.umap'})
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
OUT.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print({'protected_files':len(manifest)})
