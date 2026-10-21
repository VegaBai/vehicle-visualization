"""One-time evidence snapshot for the independent finish showcase."""
from pathlib import Path
import hashlib, json, shutil
R=Path(__file__).resolve().parents[1]
O=R/'art/YU7_TUNNEL_FLOW/reports/finish_v11'
O.mkdir(parents=True,exist_ok=True)
assert not (O/'protected_before.json').exists()
prior=R/'art/YU7_TUNNEL_FLOW/reports/roof_smooth_v10'
rows=json.loads((prior/'protected_before.json').read_text())
files={R/x['path'] for x in rows}
for row in rows:
    assert hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
files.update((R/'VehicleStudio/Content').rglob('*.uasset'))
files.update((R/'VehicleStudio/Content').rglob('*.umap'))
files.update(p for p in (R/'renders/YU7_TunnelFlow/RoofSmooth_v10').iterdir() if p.is_file())
files.update(p for p in prior.iterdir() if p.is_file())
files.update((R/'art/YU7_TUNNEL_FLOW/prepared').glob('YU7_RoofAirflow_Smooth_v10.*'))
files.add(R/'CREDITS.txt')
rows=[{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
(O/'protected_before.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
ref=R/'art/YU7_TUNNEL_FLOW/references/finish_v11'
ref.mkdir(parents=True,exist_ok=True)
shutil.copy2('C:/Users/vegab/AppData/Local/Temp/codex-clipboard-9d8ed393-9b14-40f3-a26e-613789638b21.png',ref/'user_grey_blue_gloss.png')
print(json.dumps({'protected_files':len(rows),'reference':'user_grey_blue_gloss.png'}))
