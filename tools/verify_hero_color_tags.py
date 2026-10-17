"""Validate the metadata-only remux before promoting it to the delivery filename."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'art/YU7_UNREAL/reports/hero'
DEL=ROOT/'renders/YU7_MineralHero'
FF=ROOT/'tools/vendor/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
original=DEL/'YU7_MineralTeal_5s_4K.mp4'
tagged=DEL/'YU7_MineralTeal_5s_4K_tagged.mp4'
archive=REPORT/'YU7_MineralTeal_5s_4K_before_color_tags.mp4'
assert original.exists() and tagged.exists() and not archive.exists()
def frame_hashes(name):
    return [line for line in (REPORT/name).read_text().splitlines() if line and not line.startswith('#')]
before=frame_hashes('original_frame_md5.txt')
after=frame_hashes('tagged_frame_md5.txt')
assert len(before)==120 and before==after,'Decoded pixels or frame timing differ'
p=subprocess.run([str(FF),'-hide_banner','-nostdin','-progress','pipe:1','-i',str(tagged),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
(REPORT/'tagged_decode.log').write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
assert p.returncode==0,p.stderr
assert 'yuv420p(tv, bt709/bt709/iec61966-2-1' in p.stderr,p.stderr
assert re.findall(r'^frame=(\d+)',p.stdout,re.M)[-1]=='120'
assert re.findall(r'^out_time_us=(\d+)',p.stdout,re.M)[-1]=='5000000'
assert re.findall(r'^dup_frames=(\d+)',p.stdout,re.M)[-1]=='0'
assert re.findall(r'^drop_frames=(\d+)',p.stdout,re.M)[-1]=='0'
assert (ROOT/'CREDITS.txt').read_text(encoding='utf-8-sig').strip() in p.stderr
for path in [original,tagged,archive]:assert path.resolve().is_relative_to(ROOT)
original.rename(archive)
tagged.rename(original)
report=json.loads((REPORT/'delivery_validation.json').read_text(encoding='utf-8'))
report['deliverables'][original.name]={'bytes':original.stat().st_size,'sha256':hashlib.sha256(original.read_bytes()).hexdigest()}
report['color_metadata']={'range':'limited','primaries':'bt709','transfer':'iec61966-2-1','matrix':'bt709','decoded_frames_pixel_identical_to_original_encode':120,'full_decode_after_remux':True,'duration_seconds':5.,'duplicated_frames':0,'dropped_frames':0,'original_encode_preserved':archive.relative_to(ROOT).as_posix(),'note':'H.264 VUI metadata-only remux; no video re-encoding.'}
(REPORT/'delivery_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'video':report['deliverables'][original.name],'color_metadata':report['color_metadata']},indent=2))
