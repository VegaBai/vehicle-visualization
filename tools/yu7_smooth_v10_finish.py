"""Verify the corrected delivery, preservation and exact attribution."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,subprocess,re,datetime
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports/roof_smooth_v10';D=R/'renders/YU7_TunnelFlow/RoofSmooth_v10'
FF=R/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protection=[]
for p in [O/'protected_before.json',O.parent/'art_direction_v09/protected_before.json',O.parent/'protected_before.json',O.parent/'pulse_protected_before.json',O.parent/'pulse_output_manifest_v08.json']:
    rows=read(p);rows=rows['assets'] if isinstance(rows,dict) else rows
    changed=[x['path'] for x in rows if sha(R/x['path'])!=x['sha256']];assert not changed,(p,changed)
    protection.append({'snapshot':p.relative_to(R).as_posix(),'unchanged':len(rows)})
credits=(R/'CREDITS.txt').read_bytes();assert (D/'CREDITS.txt').read_bytes()==credits
media=[]
for name,size in [('Previs_r02_1080p',[1920,1080]),('Final_r03_4K',[3840,2160])]:
    v=read(O/(name+'_validation.json'));state=read(O/(name+'_status.json'))
    assert v['resolution']==size and v['frames']==288 and v['fps']==24 and v['duration_seconds']==12
    assert v['decoded_png_frames'] and v['mp4_complete_decode'] and not v['changed_protected']
    assert state['success'] and not state['errors'];p=D/(name+'_12s.mp4');assert sha(p)==v['sha256']
    probe=subprocess.run([str(FF),'-hide_banner','-i',str(p)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
    assert f'{size[0]}x{size[1]}' in probe and '24 fps' in probe and 'Audio:' not in probe
    assert credits.decode('utf-8-sig').strip() in probe
    media.append({'path':p.relative_to(R).as_posix(),'resolution':size,'frames':288,'fps':24,'duration_seconds':12,'sha256':sha(p),'exact_attribution_in_container':True,'native_MRQ_seconds':state['duration_seconds']})
stills=[]
for frame,label in [(24,'01_CleanPaint'),(96,'02_SmoothAirflow'),(122,'03_ScanStart'),(163,'04_Handoff'),(222,'05_FullBodyClimax'),(269,'06_CleanExit'),(287,'07_FinalFrame')]:
    src=D/'Final_r03_4K'/f'Final_r03_4K_{frame:04d}.png';dst=D/f'{label}_Smooth_v10_4K.png'
    with Image.open(src) as im:im.load();assert im.size==(3840,2160)
    if dst.exists():assert sha(dst)==sha(src)
    else:shutil.copy2(src,dst)
    stills.append({'path':dst.relative_to(R).as_posix(),'source_frame':frame,'size':[3840,2160],'sha256':sha(dst),'unaltered_native_frame':True})
scene=read(O/'scene_audit.json');assert scene['saved_reload_verified'] and not scene['dirty_maps'] and not scene['dirty_content']
assert scene['protected_unchanged']==658 and scene['credits_metadata_exact']
job=read(R/'art/YU7_UNREAL/reports/ue_jobs/smooth10_07_final_audit.json');assert job['status']=='success'
key_state=read(O/'Keyframes_r01_4K_status.json');assert key_state['success'] and not key_state['errors']
keyframes=[]
for f in key_state['request']['frames']:
    p=D/'Keyframes_r01_4K'/f'Keyframes_r01_4K_{f:04d}.png'
    with Image.open(p) as im:im.load();assert im.size==(3840,2160)
    keyframes.append({'frame':f,'path':p.relative_to(R).as_posix(),'sha256':sha(p)})
log=(R/'VehicleStudio/Saved/Logs/VehicleStudio.log').read_text(encoding='utf-8',errors='replace')
checks=re.findall(r'^.*MapCheck: Map check complete: (\d+) Error\(s\), (\d+) Warning\(s\).*$' ,log,re.M)
assert checks and checks[-1]==('0','0'),checks[-1:]
assets=sorted((R/'VehicleStudio/Content/YU7/TunnelFlow/RoofSmooth_v10').rglob('*.uasset'))+sorted((R/'VehicleStudio/Content/YU7/TunnelFlow/RoofSmooth_v10').rglob('*.umap'))
assets+=sorted((R/'art/YU7_TUNNEL_FLOW/prepared').glob('*_Smooth_v10.*'))
clearance=read(O/'roof_clearance.json');assert clearance['minimum_clearance_m']>=.08
manifest={'version':'RoofSmooth_v10','validated_at':datetime.datetime.now().astimezone().isoformat(),'final_audit_job':job['id'],'map':scene['map'],'runtime':scene['runtime'],'media':media,'stills':stills,'keyframe_preflight':keyframes,'protection':protection,'minimum_sampled_clearance_m':clearance['minimum_clearance_m'],'map_check':{'errors':0,'warnings':0},'assets':[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in assets],'credits_sha256':sha(D/'CREDITS.txt'),'limitations':['Image/contact-sheet review and complete decode; no claim of realtime player viewing.','Authored visual curves, not CFD or continuous collision guarantee.','Application Credits UI and packaged/new-machine tests remain final-project delivery work.','Silent shot; mineral-teal paint retained.']}
(O/'output_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'media':len(media),'curated_stills':len(stills),'assets':len(assets),'protection':protection,'minimum_sampled_clearance_m':clearance['minimum_clearance_m']},indent=2))
