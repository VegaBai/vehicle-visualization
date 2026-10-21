"""Run each isolation in its own loaded map, never mixed-map PIE jobs."""
import unreal,json,time,traceback
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09'
D='/Game/YU7/TunnelFlow/ArtDirection_v09';E=unreal.EditorAssetLibrary
cases=json.loads((O/'prepared.json').read_text())['diagnostics'];state={'index':0,'last':0,'waiting':False,'results':[]}
def tick(delta):
    if time.monotonic()-state['last']<3:return
    if unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering():return
    state['last']=time.monotonic()
    if state['waiting']:
        name='Diagnosis_r02_'+cases[state['index']]['case']
        result=json.loads((O/(name+'_status.json')).read_text())
        if result['status']!='finished':return
        state['results'].append(result);state['index']+=1;state['waiting']=False
    if state['index']>=len(cases):
        unreal.unregister_slate_post_tick_callback(handle)
        (O/'diagnosis_batch.json').write_text(json.dumps(state['results'],indent=2),encoding='utf-8');return
    try:
        case=cases[state['index']]
        lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
        unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
        assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
        assert unreal.EditorLoadingAndSavingUtils.load_map(case['map'])
        actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
        for label,a in actors.items():
            if label.startswith('YU7_BodyQuad_') or label in ['YU7_Tunnel_SurfaceFlow','YU7_Tunnel_RoofAirflow','YU7_Tunnel_WorldWake']:
                a.modify();a.set_actor_hidden_in_game(True)
                for c in a.get_components_by_class(unreal.PrimitiveComponent):c.modify();c.set_hidden_in_game(True)
            if label.startswith('YU7_Tunnel_ScanLight_'):a.modify();a.point_light_component.modify();a.point_light_component.set_visibility(False)
        for tag in ['Front','Side','Roof']:
            c=actors['YU7_Tunnel_'+tag+'Fill'].get_component_by_class(unreal.RectLightComponent);c.modify();c.set_visibility(case['case']!='No'+tag)
        arch=actors['YU7_Tunnel_Architecture'];arch.modify()
        for c in arch.get_components_by_class(unreal.SceneComponent):
            if isinstance(c,unreal.RectLightComponent):c.modify();c.set_visibility(case['case']!='NoCeiling')
            if c.get_name()=='Tunnel_Ribs':c.modify();c.set_hidden_in_game(case['case']=='NoRibs')
        assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
        r={'name':'Diagnosis_r02_'+case['case'],'width':1280,'height':720,'temporal':8,'cases':[case]}
        (O/'render_request.json').write_text(json.dumps(r),encoding='utf-8')
        scope={'__name__':'__main__'};exec(compile((R/'tools/ue_ad_v09_render.py').read_text(),'v09_render','exec'),scope)
        state['waiting']=True
    except Exception:
        unreal.unregister_slate_post_tick_callback(handle);(O/'diagnosis_error.txt').write_text(traceback.format_exc(),encoding='utf-8')
handle=unreal.register_slate_post_tick_callback(tick)
unreal._ad_diagnosis={'handle':handle,'tick':tick,'state':state}
RESULT={'batch':'six separate loaded maps','status':'started'}
