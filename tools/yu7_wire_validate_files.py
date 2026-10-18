"""Verify protected sources and decode all final study PNGs."""
from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports'
before=json.loads((OUT/'protected_before.json').read_text(encoding='utf-8'))
changed=[]
for rel,sha in before.items():
    p=ROOT/rel
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:changed.append(rel)
images=[]
for p in sorted((ROOT/'renders/YU7_WireframeStudy/Final_v03_Confirmed').glob('*.png')):
    with Image.open(p) as im:
        im.load();images.append({'file':p.relative_to(ROOT).as_posix(),'size':list(im.size),'mode':im.mode,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
credits=(ROOT/'CREDITS.txt').read_bytes()
(ROOT/'renders/YU7_WireframeStudy/CREDITS.txt').write_bytes(credits)
assert (ROOT/'art/YU7_WIREFRAME/CREDITS.txt').read_bytes()==credits
status=json.loads((OUT/'Final_v03_Confirmed_status.json').read_text(encoding='utf-8'))
assert status['status']=='finished' and status['success'] and not status['errors']
result={'protected_files':len(before),'changed_protected_files':changed,'images':images,'exact_credit_bytes_verified':True,'mrq_success':True,'scope':'File hashes and still-image decoding; not packaged runtime or motion validation.'}
(OUT/'delivery_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
assert not changed,changed
assert len(images)>=2,'Two final views required'
assert all(i['size']==[3840,2160] for i in images)
