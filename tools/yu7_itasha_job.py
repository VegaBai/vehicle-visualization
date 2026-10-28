"""Submit explicit workspace editor jobs and wait for their result; editor-only helper."""
import argparse,json,time,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];Q=R/'art/YU7_UNREAL/reports/ue_jobs';O=R/'art/YU7_ITASHA/reports/v01'
p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('script');p.add_argument('--after-render');p.add_argument('--timeout',type=float,default=50);args=p.parse_args()
deadline=time.monotonic()+args.timeout
if args.after_render:
    while True:
        s=json.loads((O/(args.after_render+'_status.json')).read_text())
        if s.get('status')=='finished':
            assert s.get('success') and not s['errors'],s;break
        if time.monotonic()>deadline:raise TimeoutError('Waiting for render; no new job submitted')
        time.sleep(1)
assert (R/args.script).is_file();assert not (Q/(args.id+'.json')).exists(),'Job ID already used'
temp=Q/'request.itasha.tmp';temp.write_text(json.dumps({'id':args.id,'script':args.script}),encoding='utf-8');temp.replace(Q/'request.json')
while True:
    out=Q/(args.id+'.json')
    if out.exists():
        try:s=json.loads(out.read_text())
        except ValueError:s={}
        if 'status' in s:
            brief=dict(s)
            if len(json.dumps(brief.get('result',{})))>1800:brief['result']={'details_file':str(out),'keys':list(s.get('result',{}))}
            print(json.dumps(brief,ensure_ascii=True));sys.exit(0 if s['status']=='success' else 1)
    if time.monotonic()>deadline:raise TimeoutError('Job result not finished; inspect its result before retrying')
    time.sleep(.5)
