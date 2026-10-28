"""One-time preservation snapshot for the isolated itasha study."""
from pathlib import Path
import hashlib, json
R = Path(__file__).resolve().parents[1]
O = R / 'art/YU7_ITASHA/reports/v01'
O.mkdir(parents=True, exist_ok=True)
assert not (O / 'protected_before.json').exists()
prior = json.loads((R / 'art/YU7_TUNNEL_FLOW/reports/finish_v11/protected_before.json').read_text())
files = {R / row['path'] for row in prior}
for row in prior:
    assert hashlib.sha256((R / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
files.update((R / 'VehicleStudio/Content').rglob('*.uasset'))
files.update((R / 'VehicleStudio/Content').rglob('*.umap'))
files.update(p for p in (R / 'renders/YU7_TunnelFlow/FinishShowcase_v11').iterdir() if p.is_file())
files.update(p for p in (R / 'art/YU7_TUNNEL_FLOW/reports/finish_v11').iterdir() if p.is_file())
files.update((R / 'art/YU7_ITASHA/references/kimetsu_v01').glob('*.png'))
rows = [{'path': p.relative_to(R).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
(O / 'protected_before.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
print(json.dumps({'protected_files': len(rows)}))
