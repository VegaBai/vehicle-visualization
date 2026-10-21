"""Preserve all prior assets and v09 delivery files before the localized roof fix."""
from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parents[1]
O=R/'art/YU7_TUNNEL_FLOW/reports/roof_smooth_v10'
O.mkdir(parents=True,exist_ok=True)
assert not (O/'protected_before.json').exists()
old=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09'
rows=json.loads((old/'protected_before.json').read_text())
files={R/x['path'] for x in rows}
for row in rows:
    assert hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
files.update((R/'VehicleStudio/Content').rglob('*.uasset'))
files.update((R/'VehicleStudio/Content').rglob('*.umap'))
files.update(p for p in (R/'renders/YU7_TunnelFlow/ArtDirection_v09').iterdir() if p.is_file())
files.update((R/'art/YU7_TUNNEL_FLOW/prepared').glob('YU7_RoofAirflow_AD_v09.*'))
files.update(p for p in old.iterdir() if p.is_file())
rows=[{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
(O/'protected_before.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps({'protected_files':len(rows)}))
