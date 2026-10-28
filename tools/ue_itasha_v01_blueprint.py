"""Native Blueprint wrapper exposes the existing Variant Manager runtime API."""
import unreal,json
from pathlib import Path
D='/Game/YU7/Itasha_v01';E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
path=D+'/Blueprints/BP_YU7_ItashaOptions';assert not E.does_asset_exist(path)
old=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_ItashaOptions');lvs=old.get_level_variant_sets(True)
bp=unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(path,unreal.LevelVariantSetsActor);assert bp
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cls=E.load_blueprint_class(path);cdo=unreal.get_default_object(cls);cdo.set_level_variant_sets(lvs)
E.set_metadata_tag(bp,'Usage','Inherited Switch on Variant by Name: Itasha / None,Rengoku,Zenitsu,Giyu; Paint / Mineral Teal,Pearl White,Graphite. Level-local bindings.')
assert E.save_loaded_asset(bp)
new=A.spawn_actor_from_class(cls,unreal.Vector(0,0,0));new.set_level_variant_sets(lvs);new.set_actor_label('YU7_ItashaOptions_BP_New');new.set_folder_path('YU7/Itasha')
assert new.switch_on_variant_by_name('Itasha','Rengoku');assert new.switch_on_variant_by_name('Paint','Pearl White')
assert A.destroy_actor(old);new.set_actor_label('YU7_ItashaOptions')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'blueprint':path,'class_parent':'LevelVariantSetsActor','runtime_methods':['Switch on Variant by Name','Switch on Variant by Index'],'runtime_python':False,'runtime_cpp_added':False,'button_ui':'not part of current studio asset controls'}
Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01/blueprint.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
