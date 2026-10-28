"""Read-only editor/API probe; no asset changes."""
import unreal, json
from pathlib import Path
O=Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01')
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
rows=[]
for a in A.get_all_level_actors():
    if a.get_actor_label().startswith(('YU7','CAM_')):
        row={'actor':a.get_actor_label(),'class':a.get_class().get_name(),'location':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation())}
        if a.get_actor_label().startswith('YU7_VP_'):
            c=a.static_mesh_component
            row.update({'mesh':c.static_mesh.get_path_name(),'bounds':str(c.static_mesh.get_bounding_box()),'materials':[c.get_material(i).get_path_name() for i in range(c.get_num_materials())]})
        rows.append(row)
docs={n:str(getattr(unreal,n).__doc__) for n in ['DecalActor','DecalComponent','MaterialDomain','MaterialExpressionTextureSampleParameter2D','MaterialExpressionTextureCoordinate','TextureAddress']}
RESULT={'world':world.get_path_name(),'actors':rows,'dirty_maps':[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'rendering':unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering(),'docs':docs}
(O/'probe.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
