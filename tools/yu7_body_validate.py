"""Validate protected files and decode completed body-study images."""
import json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_QUAD_BODY/reports'
r=json.loads((OUT/'render_request.json').read_text(encoding='utf-8-sig'));name=r['name']
before=json.loads((OUT/'protected_before.json').read_text(encoding='utf-8'))
changed=[p for p,h in before.items() if not (ROOT/p).is_file() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
images=[]
for p in sorted((ROOT/'renders/YU7_QuadBodyStudy'/name).glob('*.png')):
    with Image.open(p) as im:
        im.load();images.append({'file':p.relative_to(ROOT).as_posix(),'size':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
status=json.loads((OUT/(name+'_status.json')).read_text(encoding='utf-8'))
assert status['status']=='finished' and status['success'] and not status['errors']
assert len(images)==len(r.get('views',['Overview','Detail','Rear']))
assert all(x['size']==[r['width'],r['height']] for x in images)
credits=(ROOT/'CREDITS.txt').read_bytes();assert (ROOT/'art/YU7_QUAD_BODY/CREDITS.txt').read_bytes()==credits
(ROOT/'renders/YU7_QuadBodyStudy/CREDITS.txt').write_bytes(credits)
result={'protected_files':len(before),'changed_protected_files':changed,'images':images,'mrq_success':True,'exact_credit_bytes_verified':True,'scope':'Static image and file integrity validation, not animation or packaged runtime.'}
(OUT/(name+'_validation.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
assert not changed,changed
print(json.dumps(result,indent=2))
