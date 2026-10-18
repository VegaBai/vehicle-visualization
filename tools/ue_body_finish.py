"""Reload saved full-body study and validate persistence without touching originals."""
import unreal,json,hashlib,math,inspect
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_QUAD_BODY/reports';DEST='/Game/YU7/QuadBodyStudy'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
VERSION=globals().get('VERSION','v03');RENDER_NAME=globals().get('RENDER_NAME','Final_v03')
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
world=unreal.EditorLoadingAndSavingUtils.load_map(DEST+'/Maps/Studio_YU7_QuadBody');assert world
actors=A.get_all_level_actors();hero=next(a for a in actors if a.get_actor_label()=='YU7_Hero')
original=hero.get_components_by_class(unreal.StaticMeshComponent);assert len(original)==121
parts=[a.static_mesh_component for a in actors if a.get_actor_label().startswith('YU7_VP_')];assert len(parts)==21
active=[c for c in original+parts if c.is_visible()];assert len(active)==121 and len({c.static_mesh.get_path_name() for c in active})==121
old=[a for a in actors if a.get_actor_label().startswith('YU7_Quad_')];assert len(old)==3
assert all(not a.static_mesh_component.is_visible() for a in old)
lines=[a for a in actors if a.get_actor_label().startswith('YU7_BodyQuad_')];assert len(lines)==3
rows=[];SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for a in lines:
    c=a.static_mesh_component;mesh=c.static_mesh;settings=SM.get_lod_build_settings(mesh,0)
    assert '/QuadBodyStudy/Meshes/'+VERSION+'/' in mesh.get_path_name()
    assert c.is_visible() and not c.hidden_in_game and not c.cast_shadow
    assert c.mobility==unreal.ComponentMobility.MOVABLE
    assert c.get_collision_profile_name()=='NoCollision' and c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
    assert a.get_attach_parent_actor()==hero
    assert settings.use_full_precision_u_vs and settings.use_high_precision_tangent_basis
    rows.append({'actor':a.get_actor_label(),'mesh':mesh.get_path_name(),'triangles':mesh.get_num_triangles(0),'parent':hero.get_actor_label(),'collision_profile':str(c.get_collision_profile_name()),'movable':True,'cast_shadow':False})
mi=unreal.load_asset(DEST+'/Materials/MI_BodyLines_IceTeal');mat=mi.parent;assert not mat.get_editor_property('wireframe')
presets=[]
for view in ['Overview','Detail','Rear']:
    seq=unreal.load_asset(DEST+'/Sequences/LS_YU7_BodyQuad_'+view);assert len(seq.get_bindings())==1
    if globals().get('CHECK_PRESETS',True):
        preset=unreal.load_asset(DEST+'/RenderPresets/MRQ_'+RENDER_NAME+'_'+view);assert preset
        settings=preset.get_all_settings();output=next(s for s in settings if isinstance(s,unreal.MoviePipelineOutputSetting));aa=next(s for s in settings if isinstance(s,unreal.MoviePipelineAntiAliasingSetting))
        assert output.output_resolution.x==3840 and output.output_resolution.y==2160 and aa.spatial_sample_count==64
        presets.append({'view':view,'preset':preset.get_path_name(),'size':[3840,2160],'samples':64})
protected=json.loads((OUT/'protected_before.json').read_text(encoding='utf-8'));changed=[p for p,h in protected.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h];assert not changed,changed
camera=next(a for a in actors if a.get_actor_label()=='CAM_YU7_BodyQuad_Overview')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key();level.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),key);level.set_level_viewport_fov(math.degrees(2*math.atan(36/(2*camera.get_cine_camera_component().current_focal_length))),key);level.editor_set_viewport_realtime(True,key);A.clear_actor_selection_set()
E.sync_browser_to_objects([DEST+'/Sequences/LS_YU7_BodyQuad_Overview']);unreal.SystemLibrary.execute_console_command(world,'MAP CHECK')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages();assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
RESULT={'map':world.get_path_name(),'version':VERSION,'saved_reload_verified':True,'original_unique_visible_vehicle_meshes':121,'old_overlay_hidden':True,'line_actors':rows,'presets':presets,'protected_files_unchanged':len(protected),'native_wireframe':False,'dirty_maps':[],'dirty_content':[],'scope':'Static views; motion and packaged runtime not tested. Final application Credits UI remains pending.'}
RESULT['runner_stopped']=False
if globals().get('STOP_RUNNER',True):
    for frame in inspect.stack():
        if Path(frame.filename).name=='ue_editor_jobs.py' and frame.function=='tick':unreal.unregister_slate_post_tick_callback(frame.frame.f_globals['HANDLE']);RESULT['runner_stopped']=True;break
    assert RESULT['runner_stopped']
    (ROOT/'art/YU7_UNREAL/reports/ue_jobs/request.json').write_text(json.dumps({'id':'body_session_closed','stop':True}),encoding='utf-8')
    if hasattr(unreal,'_yu7_body_quad_render'):delattr(unreal,'_yu7_body_quad_render')
(OUT/('final_scene_audit.json' if RESULT['runner_stopped'] else 'pre_render_audit.json')).write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
