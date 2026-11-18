"""Editor-only validation of native sequence playback in a real UE5.9 PIE world."""
import unreal,json,time,traceback
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_UNREAL/reports/ue59_runtime_r01'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.is_in_play_in_editor()
world=unreal.EditorLevelLibrary.get_game_world();assert 'UEDPIE_' in world.get_path_name()
D='/Game/YU7/TunnelFlow/FinishShowcase_v11'
seq=unreal.load_asset(D+'/Sequences/LS_YU7_FinishShowcase_v11_18s')
player,sequence_actor=unreal.LevelSequencePlayer.create_level_sequence_player(world,seq,unreal.MovieSceneSequencePlaybackSettings())
actors={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor)}
hero=actors['YU7_Hero'];roof=actors['YU7_Tunnel_RoofAirflow'];wake=actors['YU7_Tunnel_WorldWake']
assert roof.get_attach_parent_actor()==hero and wake.get_attach_parent_actor() is None
roof_components=[c for c in roof.get_components_by_class(unreal.StaticMeshComponent) if c.is_visible() and not c.get_editor_property('hidden_in_game')];assert len(roof_components)==7
for c in roof_components:
    assert c.get_editor_property('evaluate_world_position_offset')
    assert c.get_collision_profile_name()=='NoCollision'
assert sum(c.static_mesh.get_num_triangles(0) for n,a in actors.items() if n.startswith('YU7_BodyQuad_') for c in a.get_components_by_class(unreal.StaticMeshComponent))==99916
finish=unreal.load_asset(D+'/Materials/MPC_YU7_Finish_v11');flow=unreal.load_asset('/Game/YU7/TunnelFlow/Materials/MPC_TunnelFlow')
palette=json.loads((R/'art/YU7_TUNNEL_FLOW/reports/finish_v11/palette.json').read_text())
state={'status':'testing','world':world.get_path_name(),'palette_checks':[],'playback_samples':[],'roof_paths':7,'body_quad_triangles':99916,'wake_unattached':True,'errors':[]}
phase='palette';index=0;pending=None;last=0.;started=time.monotonic();run_started=None

def save(): (O/'finish_pie_audit.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
def source_frame(f):
    if f<=144:return f/7
    if f>=192:return f-144
    x=f-144;return 144/7+x/7+(6/7)*(x**3/48**2-x**4/(2*48**3))
def jump(f):
    params=unreal.MovieSceneSequencePlaybackParams();params.position_type=unreal.MovieScenePositionType.TIME;params.time=f/24;params.update_method=unreal.UpdatePositionMethod.JUMP
    player.set_playback_position(params)
def sample():
    t=player.get_current_time();f=t.time.frame_number.value+t.time.sub_frame
    v=unreal.MaterialLibrary.get_vector_parameter_value(world,finish,'PigmentColor');loc=hero.get_actor_location()
    shot=unreal.MaterialLibrary.get_scalar_parameter_value(world,flow,'ShotTime')
    return {'frame':f,'pigment':[v.r,v.g,v.b],'shot_time':shot,'hero_location':[loc.x,loc.y,loc.z]}
def tick(delta):
    global phase,index,pending,last,run_started
    if time.monotonic()-last<.25:return
    last=time.monotonic()
    try:
        if phase=='ending':
            if not level.is_in_play_in_editor():
                state['status']='passed';save();unreal.unregister_slate_post_tick_callback(unreal._ue59_finish['handle'])
            return
        assert level.is_in_play_in_editor()
        if time.monotonic()-started>180:raise TimeoutError('PIE playback exceeded 180s')
        if phase=='palette':
            if pending is not None:
                p=palette[pending];s=sample();assert max(abs(a-b) for a,b in zip(s['pigment'],p['PigmentColor']))<1e-4,(p,s)
                s['scalars']={k:unreal.MaterialLibrary.get_scalar_parameter_value(world,finish,k) for k in ['Metallic','BaseRoughness','ClearCoat','CoatRoughness']}
                for k,v in s['scalars'].items():assert abs(v-p[k])<1e-4,(k,v,p[k])
                assert abs(s['shot_time']-source_frame(p['frame'])/24)<1e-3,s
                s['name']=p['name'];state['palette_checks'].append(s);pending=None;save()
            if index<len(palette):jump(palette[index]['frame']);pending=index;index+=1
            else:jump(0);player.play();run_started=time.monotonic();phase='play'
        elif phase=='play':
            s=sample();state['playback_samples'].append(s);save()
            assert abs(s['shot_time']-source_frame(s['frame'])/24)<.1,s
            if s['frame']>=420 or not player.is_playing():
                samples=state['playback_samples'];assert len(samples)>12 and max(x['frame'] for x in samples)>=420
                assert max(x['shot_time'] for x in samples)-min(x['shot_time'] for x in samples)>10
                assert len({tuple(round(v,2) for v in x['hero_location']) for x in samples})>10
                state['playback_wall_seconds']=time.monotonic()-run_started;player.stop();phase='ending';level.editor_request_end_play()
    except Exception:
        state['status']='failed';state['errors'].append(traceback.format_exc());save()
        if level.is_in_play_in_editor():level.editor_request_end_play()
        unreal.unregister_slate_post_tick_callback(unreal._ue59_finish['handle'])
handle=unreal.register_slate_post_tick_callback(tick);unreal._ue59_finish={'handle':handle,'player':player,'actor':sequence_actor,'tick':tick,'state':state};save()
RESULT={'scheduled':'six finish plateaus and continuous native playback in PIE'}

