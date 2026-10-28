import unreal,json
from pathlib import Path
O=Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01')
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
RESULT={'rotator_doc':unreal.Rotator.__doc__,'actors':[]}
for a in A.get_all_level_actors():
    if a.get_actor_label().startswith('YU7_Itasha_'):
        c=a.get_component_by_class(unreal.DecalComponent)
        RESULT['actors'].append({'label':a.get_actor_label(),'rotation':str(a.get_actor_rotation()),'location':str(a.get_actor_location()),'size':str(c.decal_size),'scale':str(a.get_actor_scale3d()),'material':c.get_decal_material().get_path_name()})
(O/'projection_probe.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
