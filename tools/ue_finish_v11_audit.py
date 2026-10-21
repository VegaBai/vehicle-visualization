"""Persistence and native runtime-track evidence, plus all historical file hashes."""
import unreal,json,hashlib,math
exec(compile(open('C:/github2/vehicle_visualization/tools/yu7_finish_v11_common.py').read(),'finish_common','exec'))
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
seq=unreal.load_asset(SEQ)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq);unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0);unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(MAP)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
visible=[];paint=[]
for label,a in actors.items():
    if a==hero or label.startswith('YU7_VP_') or label.startswith('YU7_Tunnel_Wheel_'):
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if not c.static_mesh or not c.is_visible() or c.get_editor_property('hidden_in_game'):continue
            visible.append(c.static_mesh.get_path_name())
            for i in range(c.get_num_materials()):
                m=c.get_material(i)
                if m and m.get_path_name().startswith(D+'/Materials/M_YU7_Finish_v11.'):paint.append([label,c.get_name(),i])
assert len(visible)==121 and len(set(visible))==121
assert len(paint)==9
effects=[]
for label in ['YU7_BodyQuad_Body','YU7_BodyQuad_Mirror_L','YU7_BodyQuad_Mirror_R','YU7_Tunnel_SurfaceFlow','YU7_Tunnel_WorldWake','YU7_Tunnel_RoofAirflow']:
    a=actors[label]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if not c.is_visible() or c.get_editor_property('hidden_in_game'):continue
        m=c.get_material(0);assert m.get_path_name().startswith('/Game/YU7/TunnelFlow/ArtDirection_v09/Materials/')
        assert c.mobility==unreal.ComponentMobility.MOVABLE and c.get_collision_profile_name()=='NoCollision'
        assert not c.get_editor_property('cast_shadow')
        assert m.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_MASKED and not m.get_editor_property('wireframe')
        if label.endswith('WorldWake'):assert a.get_attach_parent_actor() is None
        else:assert a.get_attach_parent_actor()==hero
        if label.endswith('RoofAirflow'):
            assert c.static_mesh.get_path_name().startswith('/Game/YU7/TunnelFlow/RoofSmooth_v10/Meshes/')
            for p in ['evaluate_world_position_offset','evaluate_world_position_offset_in_ray_tracing','world_position_offset_writes_velocity']:assert c.get_editor_property(p)
            assert c.get_editor_property('bounds_scale')==1.5 and m.get_editor_property('max_world_position_offset_displacement')==25
        effects.append({'actor':label,'mesh':c.static_mesh.get_path_name(),'material':m.get_path_name(),'triangles':c.static_mesh.get_num_triangles(0)})
assert len([x for x in effects if x['actor']=='YU7_Tunnel_RoofAirflow'])==7
assert sum(x['triangles'] for x in effects if x['actor'].startswith('YU7_BodyQuad_'))==99916
seq=unreal.load_asset(SEQ);assert seq.get_playback_end()==432 and seq.get_display_rate().numerator==24
mpcs=[tr for tr in seq.get_tracks() if isinstance(tr,unreal.MovieSceneMaterialParameterCollectionTrack)];assert len(mpcs)==2
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
bindings=[]
for b in seq.get_bindings():
    objs=unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(seq.get_binding_id(b));assert objs,str(b.get_display_name());assert all(D+'/Maps/' in o.get_path_name() for o in objs)
    bindings.append({'name':str(b.get_display_name()),'objects':[o.get_path_name() for o in objs]})
palette=json.loads((O/'palette.json').read_text());collection=unreal.load_asset(D+'/Materials/MPC_YU7_Finish_v11');time_collection=unreal.load_asset('/Game/YU7/TunnelFlow/Materials/MPC_TunnelFlow')
samples=[]
for p in palette:
    f=p['frame'];unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(f)
    col=unreal.MaterialLibrary.get_vector_parameter_value
    v=col(world,collection,'PigmentColor')
    vals={k:unreal.MaterialLibrary.get_scalar_parameter_value(world,collection,k) for k in ['Metallic','BaseRoughness','ClearCoat','CoatRoughness']}
    actual=[v.r,v.g,v.b]
    assert max(abs(a-b) for a,b in zip(actual,p['PigmentColor']))<1e-5,(f,actual,p)
    for k,v in vals.items():assert abs(v-p[k])<1e-5,(f,k,v,p[k])
    t=unreal.MaterialLibrary.get_scalar_parameter_value(world,time_collection,'ShotTime');assert abs(t-source_frame(f)/24)<1e-4
    samples.append({'frame':f,'name':p['name'],'pigment':actual,'scalars':vals,'source_seconds':t})
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0);unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip();assert E.get_metadata_tag(seq,'Attribution')==credits
protected=json.loads((O/'protected_before.json').read_text());changed=[x['path'] for x in protected if hashlib.sha256((R/x['path']).read_bytes()).hexdigest()!=x['sha256']];assert not changed,changed
camera=actors['CAM_YU7_TunnelFlow'];level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key();level.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),key);level.set_level_viewport_fov(math.degrees(2*math.atan(36/80)),key);A.clear_actor_selection_set()
unreal.SystemLibrary.execute_console_command(world,'MAP CHECK');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages();assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
RESULT={'map':world.get_path_name(),'saved_reload_verified':True,'original_unique_visible_meshes':121,'paint_assignments':paint,'effects':effects,'bindings':bindings,'protected_unchanged':len(protected),'dirty_maps':[],'dirty_content':[],'fps':24,'frames':432,'native_finish_samples':samples,'credits_metadata_exact':True,'runtime':'Native Blueprint, Sequencer and material nodes; no runtime Python/C++.','packaged_runtime_tested':False}
(O/'scene_audit.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
