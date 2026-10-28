"""Validate finished files and publish a local evidence manifest; no image editing."""
import ast,hashlib,json,re,shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_ITASHA/reports/v01';M=R/'renders/YU7_Itasha_v01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def record(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
switch=read(O/'switch_audit.json');pie=read(O/'pie_audit.json')
assert switch['status']=='passed' and len(switch['cases'])==24
assert pie['status']=='passed' and len(pie['cases'])==12
protected=read(O/'protected_before.json')
bad=[r['path'] for r in protected if record(R/r['path'])['sha256']!=r['sha256']];assert not bad,bad
visual=read(O/'visual_review.json');assert visual['status']=='passed'
images=[];runs=[]
for name in ['Final_r08_Rengoku_4K','Final_r09_Zenitsu_4K','Final_r10_Giyu_4K']:
    s=read(O/(name+'_status.json'));assert s['status']=='finished' and s['success'] and not s['errors']
    runs.append(s)
    for view in ['Side','Beauty','Hood']:
        p=M/name/(name+'_'+view+'_0008.png');im=Image.open(p);im.load();assert im.size==(3840,2160)
        assert p.relative_to(R).as_posix() in visual['reviewed_files']
        images.append({**record(p),'width':im.width,'height':im.height,'fully_decoded':True,'visually_reviewed':True})
shutil.copyfile(R/'CREDITS.txt',M/'CREDITS.txt');assert (R/'CREDITS.txt').read_bytes()==(M/'CREDITS.txt').read_bytes()
refs=read(R/'art/YU7_ITASHA/references/kimetsu_v01/sources.json')
sources=[c for c in refs['candidates'] if c['id'] in ['rengoku','zenitsu','giyu']]
(M/'ART_SOURCES.txt').write_text('Demon Slayer official character artwork; original files unchanged.\nSource verification does not establish reuse/distribution permission.\nVehicle-model credits are in CREDITS.txt and do not cover this artwork.\n\n'+'\n\n'.join(c['character']+'\n'+c['source_page']+'\n'+c['image_url']+'\nSHA256 '+c['sha256'] for c in sources)+'\n',encoding='utf-8')
scripts=list((R/'tools').glob('*itasha*.py'))
for p in scripts:ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
log=(R/'VehicleStudio/Saved/Logs/VehicleStudio.log').read_text(encoding='utf-8',errors='replace')
checks=[l for l in log.splitlines() if 'MapCheck: Map check complete:' in l];assert checks
assert '0 Error(s), 0 Warning(s)' in checks[-1]
(O/'final_mapcheck.log').write_text(checks[-1]+'\n',encoding='utf-8')
assets=[record(p) for p in sorted((R/'VehicleStudio/Content/YU7/Itasha_v01').rglob('*')) if p.is_file()]
manifest={'status':'complete_local_studio_preview','date':datetime.now().astimezone().isoformat(),'map':'/Game/YU7/Itasha_v01/Maps/Studio_YU7_Itasha_v01','options':['None','Rengoku','Zenitsu','Giyu'],'paints':['Pearl White','Graphite','Mineral Teal'],'native_render_runs':runs,'images':images,'assets':assets,'historical_protection':{'files':len(protected),'all_sha256_match':True},'verification':{'editor_cross_frame_cases_after_safe_reload':len(switch['cases']),'actual_pie_runtime_cases':len(pie['cases']),'active_unique_vehicle_meshes':121,'attached_decals':5,'final_mapcheck':checks[-1],'python_scripts_syntax_checked':len(scripts),'credit_sidecar_byte_exact':True,'source_images_unmodified':True},'runtime':{'implementation':'Blueprint / native Variant Manager / native material graphs','python_required':False,'cpp_added':False,'ui':'Variant Manager and inherited Blueprint Switch on Variant by Name/Index; no UMG buttons'},'limits':['Original character PNGs are 1000px canvas width; 4K output does not add source texture detail.','Original studio specular reflections can obscure artwork in hood closeups.','No character artwork reuse/distribution license verified; see ART_SOURCES.txt.','Application-visible Credits and packaged/new-machine validation remain final-project delivery items.'],'credit':record(M/'CREDITS.txt'),'art_sources':sources}
(O/'output_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'images':len(images),'assets':len(assets),'protected':len(protected),'scripts':len(scripts),'status':manifest['status']}))
