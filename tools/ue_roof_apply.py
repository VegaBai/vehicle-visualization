"""One-time addition of native roof-airflow mesh, Blueprint, and material."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()==D+'/Maps/Studio_YU7_TunnelFlow.Studio_YU7_TunnelFlow'
assert not E.does_directory_exist(D+'/Meshes/RoofAirflow_v01')
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('opt=unreal.FbxImportUI()'):code.index("assert not E.does_asset_exist(D+'/Materials/MPC_TunnelFlow')")]
code=code.replace('YU7_TunnelEffects_v01.fbx','YU7_RoofAirflow_v01.fbx').replace("'destination_path':D+'/Meshes'","'destination_path':D+'/Meshes/RoofAirflow_v01'").replace('assert len(meshes)==5','assert len(meshes)==1')
exec(compile(code,'roof_fbx_import','exec'));mesh=meshes[0]
mpc=unreal.load_asset(D+'/Materials/MPC_TunnelFlow')
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('class Graph:'):code.index("g=Graph('M_TunnelGrid'")]
code=code.replace("'blend_mode':unreal.BlendMode.BLEND_ADDITIVE","'blend_mode':unreal.BlendMode.BLEND_MASKED,'opacity_mask_clip_value':.008")
exec(compile(code,'native_roof_graph_helpers','exec'))
g=Graph('M_TunnelRoofAirflow_v01',True);t=g.time();p,lane=g.uv()
phase=g.op('Frac',g.add(g.sub(g.mul(p,2.),g.mul(t,1.05)),g.mul(g.inv(lane),.23)))
streak=g.bell(g.sub(phase,.24),.10)
reveal=g.smooth(-.015,.015,g.sub(g.div(g.sub(t,1.4),2.1),p))
fade=g.inv(g.smooth(g.add(10.15,g.mul(p,.75)),g.add(10.8,g.mul(p,.75)),t))
end_taper=g.mul(g.smooth(0.,.06,p),g.inv(g.smooth(.74,1.,p)))
energy=g.mul(g.mul(g.mul(g.add(.18,g.mul(.82,streak)),reveal),fade),g.mul(end_taper,g.smooth(1.4,1.6,t)))
brightness=g.node('ScalarParameter',parameter_name='Brightness',default_value=1600.)
g.out(g.mul(g.mul(energy,brightness),(.36,.82,1.)),'EMISSIVE_COLOR');g.out(energy,'OPACITY_MASK');g.save()
E.set_metadata_tag(g.m,'Purpose','Seven illustrative airflow paths above windshield and roof, with moving highlights; not CFD simulation');E.save_loaded_asset(g.m)
path=D+'/Blueprints/BP_TunnelRoofAirflow_v01';assert not E.does_asset_exist(path)
bp=unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(path,unreal.Actor);sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
h=next(h for h in sub.k2_gather_subobject_data_for_blueprint(bp) if isinstance(lib.get_object_for_blueprint(lib.get_data(h),bp),unreal.SceneComponent));lib.get_object_for_blueprint(lib.get_data(h),bp).set_mobility(unreal.ComponentMobility.MOVABLE)
h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=h,new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(reason);assert sub.rename_subobject(h,'RoofAirflow')
c=lib.get_object_for_blueprint(lib.get_data(h),bp);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(mesh);c.set_material(0,g.m);c.set_collision_profile_name('NoCollision');c.set_editor_properties({'cast_shadow':False,'receives_decals':False})
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);E.save_loaded_asset(bp)
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
a=A.spawn_actor_from_class(E.load_blueprint_class(path),hero.get_actor_location(),hero.get_actor_rotation());a.set_actor_label('YU7_Tunnel_RoofAirflow');a.set_folder_path('TunnelFlow/Effects');assert a.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'mesh':mesh.get_path_name(),'triangles':mesh.get_num_triangles(0),'material':g.m.get_path_name(),'blueprint':path,'actor':a.get_actor_label(),'parent':hero.get_actor_label(),'timing':'1.4s reveal nose to high wake; 10.15-11.55s fade; continuous rearward highlights','native_runtime':True}
(O/'roof_assets_v01.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
