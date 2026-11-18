"""Make copied wheel Blueprint receiver exclusions persist through PIE."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12';D='/Game/YU7/TunnelFlow/ItashaShowcase_v12'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.LevelSequenceEditorBlueprintLibrary
seq=unreal.load_asset(D+'/Sequences/LS_YU7_ItashaShowcase_v12_24s');L.open_level_sequence(seq);L.set_current_time(0)
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;result=[]
for old in [a for a in A.get_all_level_actors() if a.get_actor_label().startswith('YU7_Tunnel_Wheel_')]:
    label=old.get_actor_label();path=D+'/Blueprints/BP_'+label+'_v12';assert not E.does_asset_exist(path)
    original=old.get_class().get_path_name().split('.')[0];bp=E.duplicate_asset(original,path);assert bp;seen=set()
    for h in sub.k2_gather_subobject_data_for_blueprint(bp):
        c=lib.get_object_for_blueprint(lib.get_data(h),bp)
        if not isinstance(c,unreal.PrimitiveComponent) or c.get_path_name() in seen:continue
        seen.add(c.get_path_name());c.set_editor_property('receives_decals',False)
    assert seen;assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert E.save_loaded_asset(bp)
    actor=A.spawn_actor_from_class(E.load_blueprint_class(path),old.get_actor_location(),old.get_actor_rotation());actor.set_actor_scale3d(old.get_actor_scale3d())
    parent=old.get_attach_parent_actor()
    if parent:assert actor.attach_to_actor(parent,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    b=next(b for b in seq.get_bindings() if str(b.get_display_name())==label)
    unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).replace_binding_with_actors([actor],b)
    assert A.destroy_actor(old);actor.set_actor_label(label);actor.set_folder_path('YU7/TunnelFlow/Wheels')
    result.append({'actor':label,'blueprint':path,'receiver_templates_disabled':len(seen)})
assert len(result)==4
L.set_current_time(0);L.close_level_sequence();assert E.save_loaded_asset(seq);assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'copied_wheels':result,'visual_validation':'pending'};(O/'wheel_fix.json').write_text(json.dumps(RESULT,indent=2))
