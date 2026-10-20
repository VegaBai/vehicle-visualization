import unreal,json,inspect
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
validation=json.loads((O/'Final_v06_4K_validation.json').read_text());assert validation['mp4_complete_decode'] and validation['frames']==288
preview=json.loads((O/'preview_validation.json').read_text());assert preview['complete_decode']
scope={'__name__':'__main__','AUDIT_NAME':'final_scene_audit'}
exec(compile((R/'tools/ue_tunnel_audit.py').read_text(),'ue_tunnel_audit.py','exec'),scope)
RESULT=scope['RESULT'];RESULT['final_media_validated']=True
cfg=unreal.load_asset(D+'/RenderPresets/MRQ_Final_v06_4K_Motion');assert cfg
output=next(s for s in cfg.get_all_settings() if isinstance(s,unreal.MoviePipelineOutputSetting));aa=next(s for s in cfg.get_all_settings() if isinstance(s,unreal.MoviePipelineAntiAliasingSetting))
assert output.output_resolution==unreal.IntPoint(3840,2160) and aa.temporal_sample_count==8
RESULT['render_preset']={'asset':cfg.get_path_name(),'resolution':[3840,2160],'temporal_samples':8}
unreal.EditorAssetLibrary.sync_browser_to_objects([D+'/Sequences/LS_YU7_TunnelFlow_12s'])
if hasattr(unreal,'_yu7_tunnel_render'):delattr(unreal,'_yu7_tunnel_render')
RESULT['runner_stopped']=False
for info in inspect.stack():
    if Path(info.filename).name=='ue_editor_jobs.py' and info.function=='tick':
        unreal.unregister_slate_post_tick_callback(info.frame.f_globals['HANDLE']);RESULT['runner_stopped']=True;break
assert RESULT['runner_stopped']
(R/'art/YU7_UNREAL/reports/ue_jobs/request.json').write_text(json.dumps({'id':'tunnel_session_closed','stop':True}),encoding='utf-8')
(O/'final_scene_audit.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
