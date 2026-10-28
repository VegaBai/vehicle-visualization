"""Add actual native-render previews and save the default selected option."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');D='/Game/YU7/Itasha_v01'
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
lvs=unreal.load_asset(D+'/Variants/LVS_YU7_Itasha_v01');vs=lvs.get_variant_set_by_name('Itasha')
used={}
for name,render in [('Rengoku','Final_r08_Rengoku_4K'),('Zenitsu','Final_r09_Zenitsu_4K'),('Giyu','Final_r10_Giyu_4K')]:
    path=R/'renders/YU7_Itasha_v01'/render/(render+'_Beauty_0008.png');assert path.is_file()
    variant=vs.get_variant_by_name(name);variant.set_thumbnail_from_file(str(path));assert variant.get_thumbnail()
    used[name]=str(path.relative_to(R))
assert unreal.EditorAssetLibrary.save_loaded_asset(lvs,False)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors={a.get_actor_label():a for a in A.get_all_level_actors()};manager=actors['YU7_ItashaOptions']
assert manager.switch_on_variant_by_name('Itasha','Rengoku');assert manager.switch_on_variant_by_name('Paint','Pearl White')
camera=actors['CAM_Itasha_Beauty']
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,D+'/Maps/Studio_YU7_Itasha_v01')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'thumbnails':used,'default':['Rengoku','Pearl White'],'camera':'Beauty'}
(R/'art/YU7_ITASHA/reports/v01/thumbnails.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
