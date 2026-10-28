"""Save then clear both LVS caches before loading the isolated itasha map."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
paths=['/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev','/Game/YU7/Itasha_v01/Variants/LVS_YU7_Itasha_v01']
result={}
for p in paths:
    a=unreal.load_asset(p);unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(a)
    ok=unreal.EditorLoadingAndSavingUtils.reload_packages([a.get_outermost()]);assert ok[0],str(ok);result[p]=str(ok)
world=unreal.EditorLoadingAndSavingUtils.load_map('/Game/YU7/Itasha_v01/Maps/Studio_YU7_Itasha_v01');assert world
RESULT={'reloads':result,'map':world.get_path_name(),'validation':'subsequent cross-frame audit required'}
Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01/reload.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
