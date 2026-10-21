"""One-time map, sequence and roof copies; unchanged v09 materials are reused."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/roof_smooth_v10'
D='/Game/YU7/TunnelFlow/RoofSmooth_v10';OLD='/Game/YU7/TunnelFlow/ArtDirection_v09'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
assert not E.does_directory_exist(D)
assert json.loads((O/'roof_clearance.json').read_text())['minimum_clearance_m']>=.08
assert (O/'protected_before.json').exists()
def dup(src,dst):
    assert not E.does_asset_exist(dst)
    obj=E.duplicate_asset(src,dst);assert obj;assert E.save_loaded_asset(obj);return obj
mp=D+'/Maps/Studio_YU7_TunnelFlow_Smooth_v10';sp=D+'/Sequences/LS_YU7_TunnelFlow_Smooth_v10_12s'
dup(OLD+'/Maps/Studio_YU7_TunnelFlow_AD_v09',mp)
seq=dup(OLD+'/Sequences/LS_YU7_TunnelFlow_AD_v09_12s',sp)
bp=dup(OLD+'/Blueprints/BP_TunnelRoofAirflow_v01_AD_v09',D+'/Blueprints/BP_TunnelRoofAirflow_Smooth_v10')
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(mp)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
code=(R/'tools/ue_tunnel_assets.py').read_text()
code=code[code.index('opt=unreal.FbxImportUI()'):code.index("assert not E.does_asset_exist(D+'/Materials/MPC_TunnelFlow')")]
code=code.replace('YU7_TunnelEffects_v01.fbx','YU7_RoofAirflow_Smooth_v10.fbx').replace('assert len(meshes)==5','assert len(meshes)==7')
exec(compile(code,'smooth_v10_fbx_import','exec'))
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
handles=sub.k2_gather_subobject_data_for_blueprint(bp);changed=[]
for handle in handles:
    c=lib.get_object_for_blueprint(lib.get_data(handle),bp)
    if not isinstance(c,unreal.StaticMeshComponent) or not c.static_mesh:continue
    name=c.static_mesh.get_name()
    if 'SM_RoofAD_v09_Lane' not in name:continue
    j=int(name[-1]);c.modify();c.set_static_mesh(next(m for m in meshes if m.get_name().endswith('Lane'+str(j))))
    changed.append(j)
assert sorted(changed)==list(range(7))
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
E.set_metadata_tag(bp,'Attribution',credits);assert E.save_loaded_asset(bp)
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
old=actors['YU7_Tunnel_RoofAirflow'];old.modify();old.set_actor_hidden_in_game(True);old.set_is_temporarily_hidden_in_editor(True);old.set_actor_label('YU7_Tunnel_RoofAirflow_v09_Preserved')
for c in old.get_components_by_class(unreal.PrimitiveComponent):c.modify();c.set_visibility(False);c.set_hidden_in_game(True)
roof=A.spawn_actor_from_class(E.load_blueprint_class(bp.get_path_name()),hero.get_actor_location(),hero.get_actor_rotation())
roof.set_actor_label('YU7_Tunnel_RoofAirflow');roof.set_folder_path('TunnelFlow/Effects')
assert roof.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).fix_actor_references()
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
bindings=[]
for b in seq.get_bindings():
    objs=unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(seq.get_binding_id(b));assert objs,str(b.get_display_name())
    assert all(D+'/Maps/' in o.get_path_name() for o in objs)
    bindings.append({'name':str(b.get_display_name()),'objects':[o.get_path_name() for o in objs]})
actors['SEQ_YU7_TunnelFlow'].modify();actors['SEQ_YU7_TunnelFlow'].set_sequence(seq)
E.set_metadata_tag(seq,'Attribution',credits)
unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
assert E.save_loaded_asset(seq);assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'map':mp,'sequence':sp,'roof_blueprint':bp.get_path_name(),'swapped_lanes':sorted(changed),'bindings':bindings,'materials':'Unmodified v09 native materials','visual_validation':'pending'}
(O/'prepared.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
