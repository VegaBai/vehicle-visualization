"""Save and safely reload the isolated cinematic map before final persistence audit."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
reloaded=unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()]);assert reloaded[0],str(reloaded)
world=unreal.EditorLoadingAndSavingUtils.load_map('/Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero');assert world
RESULT={'map':world.get_path_name(),'original_lvs_cache_cleared':str(reloaded),'post_reload_audit_pending':True}
Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/hero/reload_check.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
