"""Read-only v09 starting-state inventory in the live Unreal editor."""
import unreal, json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization')
O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09'
O.mkdir(parents=True,exist_ok=True)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
def component(c):
    d={'name':c.get_name(),'class':c.get_class().get_name()}
    for p in ['intensity','source_width','source_height','specular_scale','light_color','relative_location','relative_rotation','visible','hidden_in_game']:
        try:d[p]=str(c.get_editor_property(p))
        except Exception:pass
    if isinstance(c,unreal.StaticMeshComponent):
        d['materials']=[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]
        if isinstance(c,unreal.InstancedStaticMeshComponent):d['instances']=c.get_instance_count()
    return d
RESULT={'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),
 'rendering':unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering(),
 'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
 'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
 'v09_exists':unreal.EditorAssetLibrary.does_directory_exist('/Game/YU7/TunnelFlow/ArtDirection_v09'),
 'actors':{label:[component(c) for c in a.get_components_by_class(unreal.SceneComponent)] for label,a in actors.items() if label.startswith('YU7_Tunnel_') and ('Wheel' not in label)}}
(O/'starting_state.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
