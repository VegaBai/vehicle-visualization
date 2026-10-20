"""Final validation and shutdown for the roof-airflow revision editor session."""
import unreal,json,inspect
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports'
assert json.loads((O/'Previs_v07_1080p_validation.json').read_text())['mp4_complete_decode']
assert json.loads((O/'roof_output_manifest_v07.json').read_text())['native_4K_stills']==2
scope={'__name__':'__main__'};exec(compile((R/'tools/ue_roof_audit.py').read_text(),'ue_roof_audit.py','exec'),scope);RESULT=scope['RESULT']
RESULT['media_validated']=True
if hasattr(unreal,'_yu7_tunnel_render'):delattr(unreal,'_yu7_tunnel_render')
RESULT['runner_stopped']=False
for info in inspect.stack():
    if Path(info.filename).name=='ue_editor_jobs.py' and info.function=='tick':
        unreal.unregister_slate_post_tick_callback(info.frame.f_globals['HANDLE']);RESULT['runner_stopped']=True;break
assert RESULT['runner_stopped']
(R/'art/YU7_UNREAL/reports/ue_jobs/request.json').write_text(json.dumps({'id':'roof_session_closed','stop':True}),encoding='utf-8')
(O/'roof_final_audit_v07.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
