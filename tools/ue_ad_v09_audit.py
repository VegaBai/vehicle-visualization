"""Safe persisted-state audit of v09; no historical reports are overwritten."""
import unreal,json,hashlib,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_AD_v09_12s')
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq);unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0);unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0];assert unreal.EditorLoadingAndSavingUtils.load_map(D+'/Maps/Studio_YU7_TunnelFlow_AD_v09')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
visible=[]
for label,a in actors.items():
    if a==hero or label.startswith('YU7_VP_') or label.startswith('YU7_Tunnel_Wheel_'):
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.static_mesh and c.is_visible() and not c.get_editor_property('hidden_in_game'):visible.append(c.static_mesh.get_path_name())
assert len(visible)==121 and len(set(visible))==121
effects=[]
for label in ['YU7_BodyQuad_Body','YU7_BodyQuad_Mirror_L','YU7_BodyQuad_Mirror_R','YU7_Tunnel_SurfaceFlow','YU7_Tunnel_WorldWake','YU7_Tunnel_RoofAirflow']:
    a=actors[label]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if not c.is_visible() or c.get_editor_property('hidden_in_game'):continue
        m=c.get_material(0);assert m.get_path_name().startswith(D+'/Materials/')
        assert c.mobility==unreal.ComponentMobility.MOVABLE and c.get_collision_profile_name()=='NoCollision'
        assert not c.get_editor_property('cast_shadow')
        assert m.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_MASKED and not m.get_editor_property('wireframe')
        if label.endswith('WorldWake'):assert a.get_attach_parent_actor() is None
        else:assert a.get_attach_parent_actor()==hero
        if label.endswith('RoofAirflow'):
            for p in ['evaluate_world_position_offset','evaluate_world_position_offset_in_ray_tracing','world_position_offset_writes_velocity']:assert c.get_editor_property(p)
            assert c.get_editor_property('bounds_scale')==1.5
            assert m.get_editor_property('max_world_position_offset_displacement')==25
        effects.append({'actor':label,'component':c.get_name(),'mesh':c.static_mesh.get_path_name(),'material':m.get_path_name(),'triangles':c.static_mesh.get_num_triangles(0)})
assert len([x for x in effects if x['actor']=='YU7_Tunnel_RoofAirflow'])==7
assert sum(x['triangles'] for x in effects if x['actor'].startswith('YU7_BodyQuad_'))==99916
arch=actors['YU7_Tunnel_Architecture'];assert 'ArtDirection_v09' in arch.get_class().get_path_name()
lane=next(c for c in arch.get_components_by_class(unreal.InstancedStaticMeshComponent) if c.get_name()=='Tunnel_Lane');assert lane.get_instance_count()==0
seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_AD_v09_12s');assert seq.get_playback_end()==288 and seq.get_display_rate().numerator==24
tracks=[tr for tr in seq.get_tracks() if isinstance(tr,unreal.MovieSceneMaterialParameterCollectionTrack)];assert len(tracks)==1
assert tracks[0].get_editor_property('mpc').get_path_name().startswith('/Game/YU7/TunnelFlow/Materials/MPC_TunnelFlow.')
assert [k.get_value() for k in tracks[0].get_sections()[0].get_all_channels()[0].get_keys()]==[-2.,0.,12.,14.]
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
bindings=[]
for b in seq.get_bindings():
    objects=unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(seq.get_binding_id(b));assert objects,str(b.get_display_name())
    assert all(D+'/Maps/' in obj.get_path_name() for obj in objects)
    bindings.append({'name':str(b.get_display_name()),'objects':[obj.get_path_name() for obj in objects]})
unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip();assert E.get_metadata_tag(seq,'Attribution')==credits
protected=json.loads((O/'protected_before.json').read_text());changed=[x['path'] for x in protected if hashlib.sha256((R/x['path']).read_bytes()).hexdigest()!=x['sha256']];assert not changed,changed
camera=actors['CAM_YU7_TunnelFlow'];assert camera.get_cine_camera_component().current_focal_length==40
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key();level.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),key);level.set_level_viewport_fov(math.degrees(2*math.atan(36/80)),key);A.clear_actor_selection_set()
unreal.SystemLibrary.execute_console_command(world,'MAP CHECK');assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages();assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
RESULT={'map':world.get_path_name(),'saved_reload_verified':True,'original_unique_visible_meshes':121,'effects':effects,'native_sequence_bindings':bindings,'protected_unchanged':len(protected),'dirty_maps':[],'dirty_content':[],'fps':24,'frames':288,'focal_length_mm':40,'lane_instances':0,'world_wake_attached':False,'credits_metadata_exact':True,'runtime':'Native Blueprint, Sequencer, material nodes. No runtime Python/C++.','packaged_runtime_tested':False,'visible_application_credits':'Pending final application UI; sidecars and metadata do not replace it.'}
(O/'scene_audit.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
