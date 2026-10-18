"""Record the final editable assets and render hashes after verification."""
from pathlib import Path
import json,hashlib
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_QUAD_BODY/reports'
audit=json.loads((OUT/'final_scene_audit.json').read_text(encoding='utf-8'))
assert audit['saved_reload_verified'] and audit['runner_stopped']
validation=json.loads((OUT/'Final_v03_validation.json').read_text(encoding='utf-8'))
assert validation['mrq_success'] and not validation['changed_protected_files']
paths=list((ROOT/'VehicleStudio/Content/YU7/QuadBodyStudy').rglob('*.uasset'))+list((ROOT/'VehicleStudio/Content/YU7/QuadBodyStudy').rglob('*.umap'))
paths += [ROOT/'art/YU7_QUAD_BODY/YU7_BodyStudy_v03.blend',ROOT/'art/YU7_QUAD_BODY/YU7_BodyLines_v03.fbx']
paths += list((ROOT/'renders/YU7_QuadBodyStudy/Final_v03').glob('*.png'))
manifest={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)}
(OUT/'output_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print({'files':len(manifest),'bytes':sum(v['bytes'] for v in manifest.values())})
