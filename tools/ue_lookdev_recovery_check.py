import unreal,json
from pathlib import Path
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Maps/Studio_YU7.Studio_YU7'
rig=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_StudioLighting')
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
RESULT={'world':world.get_path_name(),'mesh_components':len(hero.get_components_by_class(unreal.StaticMeshComponent)),'lights':{c.get_name():{'intensity':c.intensity,'source_texture':str(c.source_texture),'size':[c.source_width,c.source_height]} for c in rig.get_components_by_class(unreal.RectLightComponent)},'variant_asset_exists':unreal.EditorAssetLibrary.does_asset_exist('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev'),'car_materials':sorted(set(c.get_material(i).get_name() for c in hero.get_components_by_class(unreal.StaticMeshComponent) for i in range(c.get_num_materials()))) }
Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/lookdev/recovery.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 64')
