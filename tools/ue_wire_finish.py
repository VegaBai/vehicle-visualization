"""Persist/reload the study, audit it, leave a useful view, stop the helper."""
import unreal,json,math,inspect,hashlib
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports';DEST='/Game/YU7/WireframeStudy'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
world=unreal.EditorLoadingAndSavingUtils.load_map(DEST+'/Maps/Studio_YU7_QuadStudy');assert world
actors=A.get_all_level_actors();hero=next(a for a in actors if a.get_actor_label()=='YU7_Hero')
original=hero.get_components_by_class(unreal.StaticMeshComponent);assert len(original)==121
parts=[a.static_mesh_component for a in actors if a.get_actor_label().startswith('YU7_VP_')];assert len(parts)==21
active=[c for c in original if c.is_visible()]+[c for c in parts if c.is_visible()]
assert len(active)==121 and len({c.static_mesh.get_path_name() for c in active})==121
line_actors=[a for a in actors if a.get_actor_label().startswith('YU7_Quad_')];assert len(line_actors)==3
rows=[];SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for a in line_actors:
    c=a.static_mesh_component;mesh=c.static_mesh;settings=SM.get_lod_build_settings(mesh,0)
    assert '/WireframeStudy/Meshes/v03/' in mesh.get_path_name()
    assert c.is_visible() and not c.hidden_in_game and not c.cast_shadow
    assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
    assert a.get_attach_parent_actor()==hero
    assert mesh.get_num_triangles(0)>0 and mesh.get_num_vertices(0)>0
    assert settings.use_full_precision_u_vs and settings.use_high_precision_tangent_basis
    rows.append({'actor':a.get_actor_label(),'mesh':mesh.get_path_name(),'render_triangles':mesh.get_num_triangles(0),'render_vertices':mesh.get_num_vertices(0),'cast_shadows':False,'collision':False,'transform':str(a.get_actor_transform())})
mat=unreal.load_asset(DEST+'/Materials/M_QuadLines');assert not mat.get_editor_property('wireframe')
mi=unreal.load_asset(DEST+'/Materials/MI_QuadLines_IceTeal')
presets=[]
for view in ['Overview','Detail']:
    seq=unreal.load_asset(DEST+'/Sequences/LS_YU7_Quad_'+view);assert len(seq.get_bindings())==1
    preset=unreal.load_asset(DEST+'/RenderPresets/MRQ_'+globals().get('RENDER_NAME','Final_v03_Confirmed')+'_'+view);assert preset
    settings=preset.get_all_settings();out=next(s for s in settings if isinstance(s,unreal.MoviePipelineOutputSetting));aa=next(s for s in settings if isinstance(s,unreal.MoviePipelineAntiAliasingSetting))
    assert out.output_resolution.x==3840 and out.output_resolution.y==2160 and aa.spatial_sample_count==64
    presets.append({'view':view,'sequence':seq.get_path_name(),'preset':preset.get_path_name(),'size':[3840,2160],'samples':64})
protected=json.loads((OUT/'protected_before.json').read_text(encoding='utf-8'));changed=[rel for rel,sha in protected.items() if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=sha];assert not changed,changed
camera=next(a for a in actors if a.get_actor_label()=='CAM_YU7_Quad_Overview')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key();level.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),key);level.set_level_viewport_fov(math.degrees(2*math.atan(36/(2*camera.get_cine_camera_component().current_focal_length))),key);level.editor_set_viewport_realtime(True,key);A.clear_actor_selection_set()
unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
E.sync_browser_to_objects([DEST+'/Sequences/LS_YU7_Quad_Overview'])
unreal.SystemLibrary.execute_console_command(world,'MAP CHECK')
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages();assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
RESULT={'map':world.get_path_name(),'saved_reload_verified':True,'original_unique_visible_vehicle_meshes':121,'line_actors':rows,'presets':presets,'line_brightness':unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mi,'LineBrightness'),'native_wireframe':False,'protected_files_unchanged':len(protected),'dirty_maps':[],'dirty_content':[],'scope':'Two static 4K views; no motion or packaged runtime validation.','visible_application_credits':'Still pending final application UI; exact sidecar and metadata retained.'}
if hasattr(unreal,'_yu7_quad_render'):delattr(unreal,'_yu7_quad_render')
RESULT['runner_stopped']=False
if globals().get('STOP_RUNNER',True):
    for info in inspect.stack():
        if Path(info.filename).name=='ue_editor_jobs.py' and info.function=='tick':unreal.unregister_slate_post_tick_callback(info.frame.f_globals['HANDLE']);RESULT['runner_stopped']=True;break
    assert RESULT['runner_stopped']
    (ROOT/'art/YU7_UNREAL/reports/ue_jobs/request.json').write_text(json.dumps({'id':'wire_session_closed','stop':True}),encoding='utf-8')
(OUT/'final_scene_audit.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
