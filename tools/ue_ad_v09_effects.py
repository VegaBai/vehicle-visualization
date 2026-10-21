"""v09 native material graphs and versioned roof Blueprint geometry."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert json.loads((O/'roof_clearance.json').read_text())['minimum_clearance_m']>=.08
mp=D+'/Maps/Studio_YU7_TunnelFlow_AD_v09'
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0];assert unreal.EditorLoadingAndSavingUtils.load_map(mp)
assert not E.does_directory_exist(D+'/Meshes/Roof_AD_v09')
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('opt=unreal.FbxImportUI()'):code.index("assert not E.does_asset_exist(D+'/Materials/MPC_TunnelFlow')")]
code=code.replace('YU7_TunnelEffects_v01.fbx','YU7_RoofAirflow_AD_v09.fbx').replace("'destination_path':D+'/Meshes'","'destination_path':D+'/Meshes/Roof_AD_v09'").replace('assert len(meshes)==5','assert len(meshes)==7')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();exec(compile(code,'ad_fbx_import','exec'))
mpc=unreal.load_asset('/Game/YU7/TunnelFlow/Materials/MPC_TunnelFlow')
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('class Graph:'):code.index("g=Graph('M_TunnelGrid'")]
code=code.replace("        assert not E.does_asset_exist(D+'/Materials/'+name)\n        self.m=T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());self.n=0", "        assert name.endswith('_AD_v09')\n        self.m=unreal.load_asset(D+'/Materials/'+name);assert self.m\n        M.delete_all_material_expressions(self.m);self.n=0")
code=code.replace("'blend_mode':unreal.BlendMode.BLEND_ADDITIVE","'blend_mode':unreal.BlendMode.BLEND_MASKED,'opacity_mask_clip_value':.003")
exec(compile(code,'ad_native_graph','exec'));node_counts={}
def finish(g,energy,brightness,color):
    b=g.node('ScalarParameter',parameter_name='Brightness',default_value=brightness)
    g.out(g.mul(g.mul(energy,b),color),'EMISSIVE_COLOR');g.out(energy,'OPACITY_MASK');g.save();node_counts[g.m.get_name()]=g.n
g=Graph('M_TunnelGrid_AD_v09',True);t=g.time();p,_=g.uv()
d=g.sub(g.div(g.sub(t,122/24),90/24),p)
reveal=g.mul(g.smooth(-.012,.012,d),g.smooth(122/24,122.5/24,t))
fade=g.inv(g.smooth(g.add(10.,g.mul(p,.5)),g.add(10.48,g.mul(p,.5)),t))
energy=g.mul(g.mul(reveal,g.add(.15,g.mul(.6,g.bell(d,.045)))),fade)
finish(g,energy,800.,(.28,.78,1.))
g=Graph('M_TunnelSurfaceFlow_AD_v09',True);t=g.time();p,l=g.uv()
def pulse(start,duration):
    d=g.sub(g.div(g.sub(t,start),duration),p)
    tail=g.mul(g.smooth(-.012,.012,d),g.pow(g.sat(g.sub(1.,g.div(d,.22))),2.))
    return g.mul(g.add(g.mul(g.bell(d,.025),.75),g.mul(tail,.25)),g.smooth(start,start+.10,t))
free=g.mul(pulse(1.5,2.7),g.inv(g.smooth(4.5,4.75,t)))
head=pulse(114/24,90/24)
energy=g.mul(g.add(free,head),g.inv(g.smooth(9.25,10.25,t)))
finish(g,energy,1700.,(.50,.85,1.))
g=Graph('M_TunnelWorldWake_AD_v09',True);t=g.time();birth,l=g.uv();age=g.sub(t,birth)
life=g.add(.16,g.mul(.14,g.smooth(8.5,9.25,t)))
tail=g.pow(g.sat(g.sub(1.,g.div(age,life))),2.)
energy=g.mul(g.mul(tail,g.smooth(-.004,.008,age)),g.mul(g.smooth(3.1,4.,t),g.inv(g.smooth(9.5,10.9,t))))
finish(g,energy,440.,(.18,.62,1.))
g=Graph('M_TunnelRoofAirflow_Pulse_v02_AD_v09',True);t=g.time();p,raw=g.uv();lane=g.inv(raw)
def sn(x):
    n=g.node('Sine',period=1.);g.link(x,n,'');return n
def phase(a,b,c):return g.add(g.sub(g.mul(p,a),g.mul(t,b)),g.mul(lane,c))
primary=g.smooth(.74,.76,lane);primary_a=g.smooth(.91,.96,lane)
weight=g.add(g.mul(g.inv(primary),g.add(.25,g.mul(lane,.08))),g.mul(primary,g.add(.75,g.mul(primary_a,.25))))
phase_p=g.op('Frac',phase(1.5,.6,.62));packet=g.add(g.mul(g.bell(g.sub(phase_p,.30),.22),.38),g.mul(g.bell(g.sub(phase_p,.30),.085),.62))
free=g.add(.018,g.mul(.982,packet))
# Existing grid/surface UV uses a five-metre domain, x=+2.5 to -2.5.
body_u=g.sub(g.mul(p,2.2),.2);progress=g.div(g.sub(t,114/24),90/24)
d=g.sub(progress,body_u);head=g.add(g.bell(d,.075),g.mul(g.smooth(-.012,.012,d),g.mul(.24,g.pow(g.sat(g.sub(1.,g.div(d,.32))),2.))))
transition=g.smooth(4.5,4.75,t)
primary_energy=g.add(g.mul(free,g.inv(transition)),g.mul(g.add(.012,head),transition))
secondary_energy=g.mul(free,g.sub(1.,g.mul(.35,g.mul(g.smooth(4.75,5.,t),g.inv(g.smooth(9.5,9.75,t))))))
shape=g.add(g.mul(primary,primary_energy),g.mul(g.inv(primary),secondary_energy))
reveal=g.mul(g.smooth(1.5,1.7,t),g.smooth(-.015,.015,g.sub(g.div(g.sub(t,1.5),2.1),p)))
taper=g.mul(g.smooth(0.,.06,p),g.inv(g.smooth(.73,1.,p)))
fade=g.inv(g.smooth(9.5,10.95,t))
energy=g.mul(g.mul(g.mul(g.mul(shape,weight),reveal),taper),fade)
color=g.add(g.mul(primary,(.68,.9,1.)),g.mul(g.inv(primary),(.18,.65,1.)))
env=g.mul(g.mul(g.smooth(.025,.12,p),g.inv(g.smooth(.9,1.,p))),g.smooth(1.5,2.,t));tail=g.smooth(.55,.78,p);stable=g.sub(1.,g.mul(primary,.3))
z=g.mul(g.mul(g.add(g.mul(g.add(2.5,g.mul(11.,tail)),sn(phase(1.5,.22,.55))),g.mul(.65,sn(phase(2.5,.18,-.5)))),env),stable)
y=g.mul(g.mul(g.mul(g.add(3.,g.mul(8.,tail)),sn(phase(1.25,.20,.65))),env),stable)
offset=g.op('AppendVector',g.op('AppendVector',0.,y),z)
transform=g.node('Transform',transform_source_type=unreal.MaterialVectorCoordTransformSource.TRANSFORMSOURCE_LOCAL,transform_type=unreal.MaterialVectorCoordTransform.TRANSFORM_WORLD)
g.link(offset,transform,'');g.out(transform,'WORLD_POSITION_OFFSET');g.m.set_editor_property('max_world_position_offset_displacement',25.)
finish(g,energy,2400.,color)
# Change only the copied Blueprint. Keep its old source component hidden as evidence.
bp=unreal.load_asset(D+'/Blueprints/BP_TunnelRoofAirflow_v01_AD_v09');bp.modify()
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
handles=sub.k2_gather_subobject_data_for_blueprint(bp)
root=next(h for h in handles if isinstance(lib.get_object_for_blueprint(lib.get_data(h),bp),unreal.SceneComponent) and not isinstance(lib.get_object_for_blueprint(lib.get_data(h),bp),unreal.PrimitiveComponent))
for h in handles:
    c=lib.get_object_for_blueprint(lib.get_data(h),bp)
    if isinstance(c,unreal.StaticMeshComponent):c.modify();c.set_visibility(False);c.set_hidden_in_game(True)
for j in range(7):
    mesh=next(m for m in meshes if m.get_name().endswith('Lane'+str(j)))
    h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(reason)
    assert sub.rename_subobject(h,'AirflowLane'+str(j));c=lib.get_object_for_blueprint(lib.get_data(h),bp)
    c.set_static_mesh(mesh);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_collision_profile_name('NoCollision');c.set_material(0,g.m)
    c.set_editor_properties({'cast_shadow':False,'receives_decals':False,'bounds_scale':1.5,'evaluate_world_position_offset':True,'evaluate_world_position_offset_in_ray_tracing':True,'world_position_offset_writes_velocity':True})
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert E.save_loaded_asset(bp)
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
old=actors['YU7_Tunnel_RoofAirflow'];old.modify();old.set_actor_hidden_in_game(True);old.set_is_temporarily_hidden_in_editor(True);old.set_actor_label('YU7_Tunnel_RoofAirflow_v08_Preserved')
a=A.spawn_actor_from_class(E.load_blueprint_class(bp.get_path_name()),hero.get_actor_location(),hero.get_actor_rotation());a.set_actor_label('YU7_Tunnel_RoofAirflow');a.set_folder_path('TunnelFlow/Effects')
assert a.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
lane_bounds=[]
for c in a.get_components_by_class(unreal.StaticMeshComponent):
    if not c.is_visible():continue
    bb=c.static_mesh.get_bounding_box();center=(bb.min+bb.max)*.5
    world_center=unreal.MathLibrary.transform_location(c.get_world_transform(),center)
    lane_bounds.append({'component':c.get_name(),'local_center':str(center),'world_center_y':world_center.y,'mesh':c.static_mesh.get_path_name()})
for label,name in [('YU7_BodyQuad_Body','M_TunnelGrid'),('YU7_BodyQuad_Mirror_L','M_TunnelGrid'),('YU7_BodyQuad_Mirror_R','M_TunnelGrid'),('YU7_Tunnel_SurfaceFlow','M_TunnelSurfaceFlow'),('YU7_Tunnel_WorldWake','M_TunnelWorldWake')]:
    c=actors[label].static_mesh_component;c.modify();c.set_material(0,unreal.load_asset(D+'/Materials/'+name+'_AD_v09'))
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'native_graph_nodes':node_counts,'body_progress':'grid/surface: (2.5-local_x_m)/5; roof: 2.2*UV.x-.2','head_frames':[114,204],'grid_frames':[122,212],'fade_complete_before_frame':264,'lane_bounds':lane_bounds,'minimum_sampled_clearance_m':json.loads((O/'roof_clearance.json').read_text())['minimum_clearance_m'],'visual_validation':'pending'}
(O/'effects_applied.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
