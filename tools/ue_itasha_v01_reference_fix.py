"""Persist the map-local options reference through an explicit editor property edit."""
import unreal,json
from pathlib import Path
D='/Game/YU7/Itasha_v01';E=unreal.EditorAssetLibrary
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=next(x for x in A.get_all_level_actors() if x.get_actor_label()=='YU7_ItashaOptions')
lvs=unreal.load_asset(D+'/Variants/LVS_YU7_Itasha_v01')
bp=unreal.load_asset(D+'/Blueprints/BP_YU7_ItashaOptions')
cdo=unreal.get_default_object(a.get_class());cdo.modify()
cdo.set_editor_property('level_variant_sets',unreal.SoftObjectPath())
bp.modify();assert E.save_loaded_asset(bp,False)
a.modify();a.set_editor_property('level_variant_sets',unreal.SoftObjectPath(lvs.get_path_name()))
assert a.get_level_variant_sets(True)==lvs
assert a.switch_on_variant_by_name('Itasha','Rengoku');assert a.switch_on_variant_by_name('Paint','Pearl White')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,D+'/Maps/Studio_YU7_Itasha_v01')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'instance_ref':a.get_level_variant_sets(True).get_path_name(),'class_default_ref':None,'forced_blueprint_and_map_save':True}
Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01/reference_fix.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
