"""Isolated vehicle Blueprint defaults make non-paint decal exclusions survive PIE."""
import unreal,json
from pathlib import Path
D='/Game/YU7/Itasha_v01';O=Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01')
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
actors={a.get_actor_label():a for a in A.get_all_level_actors()};old=actors['YU7_Hero']
path=D+'/Blueprints/BP_YU7_ItashaVehicle';assert not E.does_asset_exist(path)
before=[{'name':c.get_name(),'receives_decals':c.get_editor_property('receives_decals'),'visible':c.is_visible()} for c in old.get_components_by_class(unreal.StaticMeshComponent)]
bp=E.duplicate_asset('/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7',path);assert bp
source={c.static_mesh.get_path_name():c for c in old.get_components_by_class(unreal.StaticMeshComponent)}
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
count=0;seen=set()
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    c=lib.get_object_for_blueprint(lib.get_data(h),bp)
    if not isinstance(c,unreal.StaticMeshComponent):continue
    if c.get_path_name() in seen:continue
    seen.add(c.get_path_name())
    src=source[c.static_mesh.get_path_name()]
    for i in range(src.get_num_materials()):c.set_material(i,src.get_material(i))
    c.set_editor_properties({'receives_decals':False,'visible':src.is_visible(),'hidden_in_game':src.get_editor_property('hidden_in_game'),'cast_shadow':src.get_editor_property('cast_shadow')})
    c.set_collision_profile_name('NoCollision');count+=1
assert count==121;assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert E.save_loaded_asset(bp)
children=old.get_attached_actors()
new=A.spawn_actor_from_class(E.load_blueprint_class(path),old.get_actor_location(),old.get_actor_rotation());new.set_actor_scale3d(old.get_actor_scale3d());new.set_actor_label('YU7_ItashaVehicle_New');new.set_folder_path('YU7');new.set_editor_property('tags',old.get_editor_property('tags'))
for a in children:assert a.attach_to_actor(new,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
assert A.destroy_actor(old);new.set_actor_label('YU7_Hero')
assert all(not c.get_editor_property('receives_decals') for c in new.get_components_by_class(unreal.StaticMeshComponent))
# The upright direction is roll +90 with UE's decal UV convention.
for side,yaw in [('Left',-90),('Right',90)]:
    actors['YU7_Itasha_'+side].set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=90),True)
    actors['YU7_Itasha_Sweep_'+side].set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=90),True)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'copied_blueprint':path,'templates':count,'all_bp_receivers_disabled':True,'attached_children':len(children),'before':before,'side_roll':90,'visual_check':'pending'}
(O/'receiver_fix.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
