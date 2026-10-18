import unreal,json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_WIREFRAME/reports')
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
RESULT={'world':world.get_path_name(),'dirty_maps':[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'actors':[]}
for a in A.get_all_level_actors():
    if a.get_actor_label()=='YU7_Hero' or isinstance(a,unreal.CineCameraActor) or 'YU7_VP_' in a.get_actor_label():
        RESULT['actors'].append({'label':a.get_actor_label(),'transform':str(a.get_actor_transform()),'meshes':[{'name':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'transform':str(c.get_world_transform())} for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and '040' in c.static_mesh.get_name()]})
(OUT/'ue_before.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
