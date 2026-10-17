import unreal,json
from pathlib import Path
root=Path('C:/github2/vehicle_visualization')
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
asset=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
# Serialization/reload drops the engine's non-UPROPERTY cached component addresses.
# Do this before tearing down the old world, while all old references are valid.
reload_result=unreal.EditorLoadingAndSavingUtils.reload_packages([asset.get_outermost()])
assert reload_result[0],str(reload_result)
world=unreal.EditorLoadingAndSavingUtils.load_map('/Game/YU7/Maps/Studio_YU7')
assert world
# Validation runs in a separate subsequent task after this world has settled.
RESULT={'reloaded_map':world.get_path_name(),'variant_asset_reload':str(reload_result),'validation_pending':True}
(root/'art/YU7_UNREAL/reports/lookdev/reload.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
