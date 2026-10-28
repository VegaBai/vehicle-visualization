"""Show the finished native Variant Manager options without altering the saved scene."""
import unreal,json
from pathlib import Path
D='/Game/YU7/Itasha_v01';lvs=unreal.load_asset(D+'/Variants/LVS_YU7_Itasha_v01')
assert lvs
thumbnails={}
for name in ['Rengoku','Zenitsu','Giyu']:
    v=lvs.get_variant_set_by_name('Itasha').get_variant_by_name(name)
    assert v.get_thumbnail();thumbnails[name]=v.get_thumbnail().get_name()
actors={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
assert actors['YU7_ItashaOptions'].get_level_variant_sets(True)==lvs
camera=actors['CAM_Itasha_Beauty']
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
opened=unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([lvs])
RESULT={'native_option_editor_open_requested':bool(opened),'saved_thumbnails':thumbnails,'instance_reference_valid':True}
Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01/options_ready.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
