"""Restore duplicated sequence metadata and sample native cue evaluation."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_AD_v09_12s');E=unreal.EditorAssetLibrary
old=str(E.get_metadata_tag(seq,'Attribution'));credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip();E.set_metadata_tag(seq,'Attribution',credits);E.save_loaded_asset(seq)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in A.get_all_level_actors()};world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith(D+'/Maps/')
mpc=unreal.load_asset('/Game/YU7/TunnelFlow/Materials/MPC_TunnelFlow');samples=[]
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
for f in [0,24,35,36,96,114,122,163,204,212,222,240,264,269,287]:
    unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(f)
    t=unreal.MaterialLibrary.get_scalar_parameter_value(world,mpc,'ShotTime');x=actors['YU7_Hero'].get_actor_location().x
    samples.append({'frame':f,'mpc_seconds':t,'hero_world_x_cm':x,'expected_x_cm':-f*62.5,'camera_world_location':str(actors['CAM_YU7_TunnelFlow'].get_actor_location())})
    assert abs(t-f/24)<1e-4 and abs(x+f*62.5)<.1,samples[-1]
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0);unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence();unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'previous_metadata':old,'credits_restored':True,'native_time_and_translation_samples':samples};(O/'native_cue_samples.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
