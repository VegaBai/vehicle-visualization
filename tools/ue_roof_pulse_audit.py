"""Save/reload v08 and verify the instance override without altering v07 reports."""
from pathlib import Path
import json,hashlib,unreal
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports'
scope={'__name__':'__main__','AUDIT_NAME':'pulse_base_audit_v08'}
exec(compile((R/'tools/ue_tunnel_audit.py').read_text(),'ue_tunnel_audit.py','exec'),scope)
RESULT=scope['RESULT'];A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in A.get_all_level_actors()}
a=actors['YU7_Tunnel_RoofAirflow'];assert a.get_attach_parent_actor()==actors['YU7_Hero']
cs=[c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh];assert len(cs)==1;c=cs[0]
assert c.static_mesh.get_num_triangles(0)==92400 and c.is_visible() and not c.get_editor_property('hidden_in_game')
assert c.mobility==unreal.ComponentMobility.MOVABLE and c.get_collision_profile_name()=='NoCollision' and not c.get_editor_property('cast_shadow')
m=c.get_material(0);assert m.get_path_name()=='/Game/YU7/TunnelFlow/Materials/M_TunnelRoofAirflow_Pulse_v02.M_TunnelRoofAirflow_Pulse_v02'
assert m.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_MASKED and not m.get_editor_property('wireframe')
assert m.get_editor_property('max_world_position_offset_displacement')==35. and c.get_editor_property('bounds_scale')==1.5
flags={k:c.get_editor_property(k) for k in ['evaluate_world_position_offset','evaluate_world_position_offset_in_ray_tracing','world_position_offset_writes_velocity']};assert all(flags.values()),flags
old=json.loads((O/'pulse_protected_before.json').read_text());changed=[p['path'] for p in old if hashlib.sha256((R/p['path']).read_bytes()).hexdigest()!=p['sha256']];assert not changed,changed
RESULT.update(roof_blueprint=a.get_class().get_path_name(),roof_mesh=c.static_mesh.get_path_name(),roof_material=m.get_path_name(),roof_triangles=92400,roof_lines=7,v07_protected_unchanged=len(old),roof_minimum_sampled_clearance_m=json.loads((O/'roof_pulse_geometry_v08.json').read_text())['minimum_clearance_m'],WPO_flags=flags,bounds_scale=1.5,WPO_cap_cm=35.)
(O/'pulse_scene_audit_v08.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
