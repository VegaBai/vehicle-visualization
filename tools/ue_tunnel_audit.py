"""Save/reload isolated shot, verify durable assembly and native sequence wiring."""
import unreal,json,hashlib,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow';E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_12s');unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq);unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0);unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs);assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(D+'/Maps/Studio_YU7_TunnelFlow')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
visible=[];effects=[]
for a in actors.values():
    if a==hero or a.get_actor_label().startswith('YU7_VP_') or a.get_actor_label().startswith('YU7_Tunnel_Wheel_'):
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.static_mesh and c.is_visible() and not c.get_editor_property('hidden_in_game'):visible.append(c.static_mesh.get_path_name())
assert len(visible)==121 and len(set(visible))==121,(len(visible),len(set(visible)))
assert len(hero.get_components_by_class(unreal.StaticMeshComponent))==121
for label in ['YU7_BodyQuad_Body','YU7_BodyQuad_Mirror_L','YU7_BodyQuad_Mirror_R','YU7_Tunnel_SurfaceFlow','YU7_Tunnel_WorldWake']:
    a=actors[label];c=a.static_mesh_component;m=c.get_material(0)
    assert c.is_visible() and not c.get_editor_property('hidden_in_game')
    assert c.get_collision_profile_name()=='NoCollision' and c.mobility==unreal.ComponentMobility.MOVABLE
    assert not c.get_editor_property('cast_shadow')
    assert m.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_MASKED and not m.get_editor_property('wireframe')
    if label.endswith('WorldWake'):assert a.get_attach_parent_actor() is None
    else:assert a.get_attach_parent_actor()==hero
    effects.append({'actor':label,'mesh':c.static_mesh.get_path_name(),'material':m.get_path_name(),'parent':a.get_attach_parent_actor().get_actor_label() if a.get_attach_parent_actor() else None,'triangles':c.static_mesh.get_num_triangles(0)})
for label in ['FL','FR','RL','RR']:
    a=actors['YU7_Tunnel_Wheel_'+label];assert a.get_attach_parent_actor()==hero;assert len(a.get_components_by_class(unreal.StaticMeshComponent))==6
seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_12s');assert seq.get_playback_end()==288 and seq.get_display_rate().numerator==24
tracks=[tr for tr in seq.get_tracks() if isinstance(tr,unreal.MovieSceneMaterialParameterCollectionTrack)];assert len(tracks)==1
keys=tracks[0].get_sections()[0].get_all_channels()[0].get_keys();assert [k.get_value() for k in keys]==[-2.,0.,12.,14.]
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip();assert E.get_metadata_tag(seq,'Attribution')==credits
protected=json.loads((O/'protected_before.json').read_text());changed=[p['path'] for p in protected if hashlib.sha256((R/p['path']).read_bytes()).hexdigest()!=p['sha256']];assert not changed,changed
camera=actors['CAM_YU7_TunnelFlow'];level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key();level.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),key);level.set_level_viewport_fov(math.degrees(2*math.atan(36/80)),key);A.clear_actor_selection_set()
# Preserve the user's realtime setting. UE 5.8's True setter removes an override
# and raises an ensure when this script did not previously install that override.
unreal.SystemLibrary.execute_console_command(world,'MAP CHECK');unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages();assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
RESULT={'map':world.get_path_name(),'saved_reload_verified':True,'original_unique_visible_meshes':121,'wheel_blueprints':4,'effects':effects,'fps':24,'frames':288,'protected_files_unchanged':len(protected),'dirty_maps':[],'dirty_content':[],'credits_metadata_exact':True,'runtime':'Native Blueprint components, native Sequencer and material graphs; editor Python only','packaged_runtime_tested':False,'visible_application_credits':'Pending final application UI; metadata and exact sidecars do not replace it.'}
(O/(globals().get('AUDIT_NAME','scene_audit')+'.json')).write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
