import unreal,json
from pathlib import Path
RESULT={
    'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),
    'rendering':unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering(),
    'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
    'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
    'v10_exists':unreal.EditorAssetLibrary.does_directory_exist('/Game/YU7/TunnelFlow/RoofSmooth_v10')
}
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/roof_smooth_v10/starting_state.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
