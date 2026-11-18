"""Validate native sequence states in standard PIE, then end PIE."""
import unreal,json,time,traceback
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.is_in_play_in_editor()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
seq=unreal.load_asset('/Game/YU7/TunnelFlow/ItashaShowcase_v12/Sequences/LS_YU7_ItashaShowcase_v12_24s')
player,seqactor=unreal.LevelSequencePlayer.create_level_sequence_player(world,seq,unreal.MovieSceneSequencePlaybackSettings())
actors=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor);decals=[a for a in actors if isinstance(a,unreal.DecalActor)];hero=next(a for a in actors if a.get_class().get_name()=='BP_YU7_ItashaFilm_v12_C')
assert len(decals)==15;assert all(a.get_attach_parent_actor()==hero for a in decals)
assert all(not c.get_editor_property('receives_decals') for c in hero.get_components_by_class(unreal.StaticMeshComponent))
wheels=[a for a in actors if a.get_class().get_name().startswith('BP_YU7_Tunnel_Wheel_')];assert len(wheels)==4
assert all(not c.get_editor_property('receives_decals') for a in wheels for c in a.get_components_by_class(unreal.StaticMeshComponent))
frames=[0,150,191,192,198,239,240,246,287,288,432,510,575]
state={'status':'running','world':world.get_path_name(),'samples':[],'errors':[]};index=[0];pending=[None];last=[0.]
def save(): (O/'pie_audit.json').write_text(json.dumps(state,indent=2))
def tick(dt):
    if time.monotonic()-last[0]<.3:return
    last[0]=time.monotonic()
    try:
        if pending[0] is not None:
            f=pending[0];shown=[a.get_name() for a in decals if not a.get_editor_property('hidden')]
            assert len(shown)==(5 if 150<=f<192 or 198<=f<240 or 246<=f<288 else 0),(f,shown)
            state['samples'].append({'frame':f,'visible_decals':len(shown),'hero_x':hero.get_actor_location().x});pending[0]=None;index[0]+=1;save()
        if index[0]==len(frames):
            player.stop();state['status']='passed';save();unreal.unregister_slate_post_tick_callback(handle);level.editor_request_end_play();return
        f=frames[index[0]];params=unreal.MovieSceneSequencePlaybackParams(frame=unreal.FrameTime(unreal.FrameNumber(f)),position_type=unreal.MovieScenePositionType.FRAME,update_method=unreal.UpdatePositionMethod.JUMP)
        player.set_playback_position(params);pending[0]=f
    except Exception:
        state['status']='failed';state['errors'].append(traceback.format_exc());save();unreal.unregister_slate_post_tick_callback(handle);level.editor_request_end_play()
save();handle=unreal.register_slate_post_tick_callback(tick)
unreal._v12_pie={'player':player,'actor':seqactor,'tick':tick,'handle':handle}
RESULT={'started':True}
