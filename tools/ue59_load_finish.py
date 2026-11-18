import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization'); O=R/'art/YU7_UNREAL/reports/ue59_runtime_r01'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
for p in ['/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev','/Game/YU7/Itasha_v01/Variants/LVS_YU7_Itasha_v01']:
    a=unreal.load_asset(p);unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(a)
    assert unreal.EditorLoadingAndSavingUtils.reload_packages([a.get_outermost()])[0]
D='/Game/YU7/TunnelFlow/FinishShowcase_v11'
assert unreal.EditorLoadingAndSavingUtils.load_map(D+'/Maps/Studio_YU7_FinishShowcase_v11')
RESULT={'map':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),'safe_lvs_clear':True,'playback_params_doc':unreal.MovieSceneSequencePlaybackParams.__doc__,'player_doc':unreal.LevelSequencePlayer.create_level_sequence_player.__doc__}
