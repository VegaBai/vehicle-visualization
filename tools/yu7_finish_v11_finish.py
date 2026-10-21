"""Final delivery manifest, exact credits, curated unaltered native stills."""
from pathlib import Path
import hashlib,json,subprocess,shutil
from PIL import Image
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports/finish_v11';D=R/'renders/YU7_TunnelFlow/FinishShowcase_v11'
ff=R/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((O/'scene_audit.json').read_text());assert audit['saved_reload_verified'] and audit['protected_unchanged']==708
review=json.loads((O/'visual_review.json').read_text());assert review['final_covered_frames']==432
media=[]
for name in ['Previs_r03_1080p','Final_r04_4K']:
    for suffix in ['_validation.json','_titles_validation.json']:
        q=json.loads((O/(name+suffix)).read_text(encoding='utf-8'))
        p=Path(q['video']);p=p if p.is_absolute() else R/p
        assert p.exists() and sha(p)==q['sha256']
        assert q['frames']==432 and q['duration_seconds']==18
        raw=subprocess.run([str(ff),'-hide_banner','-nostdin','-i',str(p),'-f','ffmetadata','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
        assert raw.returncode==0 and credits in raw.stdout
        assert f"{q['resolution'][0]}x{q['resolution'][1]}" in raw.stderr and '24 fps' in raw.stderr
        media.append({'path':p.relative_to(R).as_posix(),'resolution':q['resolution'],'frames':432,'fps':24,'duration_seconds':18,'sha256':sha(p),'exact_attribution_in_container':True,'labeled':'titles' in suffix})
shutil.copy2(R/'CREDITS.txt',D/'CREDITS.txt');assert sha(R/'CREDITS.txt')==sha(D/'CREDITS.txt')
stills=[]
names=['GreyBlue_Gloss','Blue_Metallic','Opal_Pearl','Graphite_Matte','Grey_Ceramic','MineralTeal_Return','Flow_Handoff','FullBody_Climax','Clean_Final']
for i,(f,n) in enumerate(zip([12,42,72,102,138,180,310,366,431],names),1):
    src=D/'Final_r04_4K'/f'Final_r04_4K_{f:04d}.png';p=D/f'{i:02d}_{n}_v11_4K.png'
    if not p.exists():shutil.copy2(src,p)
    assert sha(src)==sha(p)
    with Image.open(p) as im:im.load();assert im.size==(3840,2160)
    stills.append({'path':p.relative_to(R).as_posix(),'source_frame':f,'size':[3840,2160],'unaltered_native_frame':True,'sha256':sha(p)})
rows=json.loads((O/'protected_before.json').read_text());changed=[x['path'] for x in rows if sha(R/x['path'])!=x['sha256']];assert not changed,changed
assets=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in sorted((R/'VehicleStudio/Content/YU7/TunnelFlow/FinishShowcase_v11').rglob('*')) if p.is_file()]
out={'version':'FinishShowcase_v11','map':audit['map'],'sequence':'/Game/YU7/TunnelFlow/FinishShowcase_v11/Sequences/LS_YU7_FinishShowcase_v11_18s','runtime':audit['runtime'],'media':media,'stills':stills,'assets':assets,'protected_unchanged':len(rows),'credits_sha256':sha(R/'CREDITS.txt'),'visual_review':'visual_review.json','limits':['Silent shot.','Art-directed finish representations; not measured colour codes or spectra.','Editorial labels are a separate encoded version; clean native frame master retained.','Application Credits UI and packaged/new-machine validation remain final-project delivery items.','Authored flow and quad visualization, not CFD or recovered source topology.']}
(O/'output_manifest.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'media':len(media),'stills':len(stills),'assets':len(assets),'protected':len(rows)}))
