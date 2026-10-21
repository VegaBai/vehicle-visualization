"""Export actual native instance boxes for offline 96 Hz camera/LOS checks."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09'
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);arch=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Tunnel_Architecture')
assert 'ArtDirection_v09' in arch.get_class().get_path_name()
boxes=[]
def xyz(v):return [v.x,v.y,v.z]
for c in arch.get_components_by_class(unreal.InstancedStaticMeshComponent):
    if not c.is_visible() or c.get_editor_property('hidden_in_game'):continue
    bb=c.static_mesh.get_bounding_box();center=(bb.min+bb.max)*.5;half=(bb.max-bb.min)*.5
    for i in range(c.get_instance_count()):
        tr=c.get_instance_transform(i,world_space=True);p=unreal.MathLibrary.transform_location(tr,center)
        axes=[unreal.MathLibrary.transform_location(tr,center+v)-p for v in [unreal.Vector(1,0,0),unreal.Vector(0,1,0),unreal.Vector(0,0,1)]]
        boxes.append({'component':c.get_name(),'instance':i,'center':xyz(p),'axes':[xyz(v) for v in axes],'half':xyz(half)})
(O/'environment_boxes.json').write_text(json.dumps(boxes),encoding='utf-8')
RESULT={'actual_visible_native_boxes':len(boxes)}
