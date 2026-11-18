"""Build the final delivery manifest only after actual renders/reviews pass."""
from pathlib import Path
import json,hashlib,shutil,ast
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12';D=R/'renders/YU7_TunnelFlow/ItashaShowcase_v12'
review=json.loads((O/'visual_review.json').read_text(encoding='utf-8'));assert review['preview']['status']=='passed' and review['final_4k']['status']=='passed'
renders=[]
for name in ['Previs_r02_1080p','Final_r03_4K']:
    s=json.loads((O/(name+'_status.json')).read_text(encoding='utf-8'));v=json.loads((O/(name+'_validation.json')).read_text(encoding='utf-8'));assert s['success'] and not s['errors'];assert all(x['complete_decode'] for x in v['outputs'])
    renders.append({'name':name,'seconds':s['duration_seconds'],'verification':v})
stills=[]
for f,label in [(0,'GreyBlue'),(30,'MetallicBlue'),(60,'PearlWhite'),(90,'Graphite'),(120,'CeramicGloss'),(170,'Rengoku'),(216,'Zenitsu'),(264,'Giyu'),(432,'RoofFlow'),(510,'FullQuad'),(564,'CleanExit')]:
    src=D/'frames/Final_r03_4K'/f'Final_r03_4K_{f:04d}.png';dst=D/f'{f:04d}_{label}_v12_4K.png'
    with Image.open(src) as im:im.load();assert im.size==(3840,2160)
    if not dst.exists():shutil.copy2(src,dst)
    assert dst.read_bytes()==src.read_bytes();stills.append(dst)
protected=json.loads((O/'protected_before.json').read_text(encoding='utf-8-sig'));changed=[x['path'] for x in protected if hashlib.sha256((R/x['path']).read_bytes()).hexdigest()!=x['sha256']];assert not changed,changed
assert (D/'CREDITS.txt').read_bytes()==(R/'CREDITS.txt').read_bytes()
scripts=list((R/'tools').glob('*v12*.py'))
for p in scripts:ast.parse(p.read_text(encoding='utf-8-sig'))
files=list(D.glob('*.mp4'))+stills+[D/'CREDITS.txt',D/'ART_SOURCES.txt']+list((R/'VehicleStudio_UE59/Content/YU7/TunnelFlow/ItashaShowcase_v12').rglob('*.uasset'))+list((R/'VehicleStudio_UE59/Content/YU7/TunnelFlow/ItashaShowcase_v12').rglob('*.umap'))
manifest={'status':'verified_local_delivery','date':'2026-11-18','engine':'5.9.0','frames':576,'fps':24,'duration_seconds':24,'native_final_resolution':[3840,2160],'renders':renders,'protected_unchanged':len(protected),'changed_protected':[],'parsed_scripts':len(scripts),'credits_sidecar_byte_exact':True,'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'limits':['Silent','No packaged/new-machine validation','Character artwork reuse/distribution rights not verified; existing source files unchanged','Art-directed finishes and illustrative airflow, not physical measurement/CFD','No human aesthetic acceptance claimed']}
(O/'output_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'files':len(files),'videos':len(list(D.glob('*.mp4'))),'stills':len(stills),'protected':len(protected),'scripts':len(scripts)}))
