"""Extend baseline save/reload checks with durable roof Blueprint checks."""
from pathlib import Path
import json,hashlib,unreal
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports'
scope={'__name__':'__main__','AUDIT_NAME':'roof_scene_audit'}
exec(compile((R/'tools/ue_tunnel_audit.py').read_text(),'ue_tunnel_audit.py','exec'),scope)
RESULT=scope['RESULT'];A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in A.get_all_level_actors()}
a=actors['YU7_Tunnel_RoofAirflow'];assert a.get_attach_parent_actor()==actors['YU7_Hero']
cs=[c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh];assert len(cs)==1;c=cs[0]
assert c.static_mesh.get_num_triangles(0)==92400 and c.is_visible() and not c.get_editor_property('hidden_in_game')
assert c.mobility==unreal.ComponentMobility.MOVABLE and c.get_collision_profile_name()=='NoCollision' and not c.get_editor_property('cast_shadow')
m=c.get_material(0);assert m.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_MASKED and not m.get_editor_property('wireframe')
old=json.loads((O/'roof_protected_before.json').read_text());changed=[p['path'] for p in old if hashlib.sha256((R/p['path']).read_bytes()).hexdigest()!=p['sha256']];assert not changed,changed
RESULT.update(roof_blueprint=a.get_class().get_path_name(),roof_mesh=c.static_mesh.get_path_name(),roof_material=m.get_path_name(),roof_triangles=92400,roof_lines=7,v06_protected_unchanged=len(old),roof_min_clearance_m=json.loads((O/'roof_geometry_v01.json').read_text())['min_clearance_m'])
(O/'roof_scene_audit.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
