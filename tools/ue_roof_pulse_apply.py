"""Native material-only pulse and traveling deformation; v07 assets remain intact."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
assert json.loads((O/'roof_pulse_geometry_v08.json').read_text())['minimum_clearance_m']>.04
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()==D+'/Maps/Studio_YU7_TunnelFlow.Studio_YU7_TunnelFlow'
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert E.does_asset_exist(D+'/Maps/Studio_YU7_TunnelFlow_BeforePulse_v07')
mpc=unreal.load_asset(D+'/Materials/MPC_TunnelFlow')
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('class Graph:'):code.index("g=Graph('M_TunnelGrid'")]
code=code.replace("'blend_mode':unreal.BlendMode.BLEND_ADDITIVE","'blend_mode':unreal.BlendMode.BLEND_MASKED,'opacity_mask_clip_value':.003")
exec(compile(code,'pulse_graph_helpers','exec'))
g=Graph('M_TunnelRoofAirflow_Pulse_v02',True);t=g.time();p,raw_lane=g.uv();lane=g.inv(raw_lane)
def sn(x):
    n=g.node('Sine',period=1.);g.link(x,n,'');return n
def phase(a,b,c):return g.add(g.sub(g.mul(p,a),g.mul(t,b)),g.mul(lane,c))
# Soft bright packets and independently phased breathing; very low background glow.
phase_p=g.op('Frac',g.add(phase(1.55,.68,.52),g.mul(sn(g.mul(lane,1.7)),.07)))
d=g.sub(phase_p,.32)
packet=g.add(g.mul(g.bell(d,.23),.35),g.mul(g.bell(d,.09),.65))
breath=g.add(.28,g.mul(.72,g.pow(g.add(.5,g.mul(.5,sn(g.sub(g.mul(t,.36),g.mul(lane,.7))))),2.2)))
reveal=g.smooth(-.015,.015,g.sub(g.div(g.sub(t,1.4),2.1),p))
fade=g.inv(g.smooth(g.add(10.15,g.mul(p,.75)),g.add(10.8,g.mul(p,.75)),t))
taper=g.mul(g.smooth(0.,.06,p),g.inv(g.smooth(.74,1.,p)))
energy=g.mul(g.mul(g.mul(g.add(.007,g.mul(.993,g.mul(packet,breath))),reveal),fade),g.mul(taper,g.smooth(1.4,1.6,t)))
brightness=g.node('ScalarParameter',parameter_name='Brightness',default_value=2200.)
g.out(g.mul(g.mul(energy,brightness),(.30,.80,1.)),'EMISSIVE_COLOR');g.out(energy,'OPACITY_MASK')
# Gentle near-roof undulation grows into a loose high wake. All displacement is cm.
env=g.mul(g.mul(g.smooth(.025,.12,p),g.inv(g.smooth(.9,1.,p))),g.smooth(1.4,2.,t))
z=g.mul(g.add(g.mul(g.add(5.,g.mul(17.,g.smooth(.48,.84,p))),sn(phase(1.8,.28,.63))),g.mul(3.,sn(phase(3.4,.17,-.81)))),env)
y=g.mul(g.mul(g.add(6.,g.mul(13.,g.smooth(.45,.8,p))),sn(phase(1.45,.23,.91))),env)
xy=g.op('AppendVector',0.,y);offset=g.op('AppendVector',xy,z)
transform=g.node('Transform',transform_source_type=unreal.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_LOCAL,transform_type=unreal.MaterialVectorCoordTransform.TRANSFORM_WORLD)
g.link(offset,transform,'');g.out(transform,'WORLD_POSITION_OFFSET')
g.m.set_editor_property('max_world_position_offset_displacement',35.);g.save()
E.set_metadata_tag(g.m,'Motion','Native MPC ShotTime pulse plus two vertical waves and one lateral wave; authored illustrative airflow');E.save_loaded_asset(g.m)
a=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Tunnel_RoofAirflow');c=next(c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh)
c.modify();c.set_material(0,g.m);c.set_editor_properties({'bounds_scale':1.5,'evaluate_world_position_offset':True,'evaluate_world_position_offset_in_ray_tracing':True,'world_position_offset_writes_velocity':True})
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'material':g.m.get_path_name(),'actor':a.get_actor_label(),'base_glow':.007,'brightness':2200,'pulse_cycles_per_second':.68,'breathing_cycles_per_second':.36,'WPO_cap_cm':35,'component_bounds_scale':1.5,'native_graph_nodes':g.n,'geometry_unchanged':True,'minimum_sampled_clearance_m':json.loads((O/'roof_pulse_geometry_v08.json').read_text())['minimum_clearance_m']}
(O/'roof_pulse_material_v08.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
