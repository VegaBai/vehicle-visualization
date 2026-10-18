"""Import only new quad line assets and assemble only in the isolated map."""
import unreal,json,math
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports'
DEST='/Game/YU7/WireframeStudy';E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==DEST+'/Maps/Studio_YU7_QuadStudy.Studio_YU7_QuadStudy'
assert not E.does_directory_exist(DEST+'/Meshes/v01')
opt=unreal.FbxImportUI();opt.set_editor_properties({'automated_import_should_detect_type':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_STATIC_MESH,'import_as_skeletal':False,'import_mesh':True,'import_materials':False,'import_textures':False})
opt.static_mesh_import_data.set_editor_properties({'combine_meshes':False,'auto_generate_collision':False,'generate_lightmap_u_vs':False,'convert_scene':True,'convert_scene_unit':True,'force_front_x_axis':False,'import_uniform_scale':1.,'transform_vertex_to_absolute':True,'build_nanite':False,'normal_import_method':unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS})
task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(ROOT/'art/YU7_WIREFRAME/YU7_QuadLines_v01.fbx'),'destination_path':DEST+'/Meshes/v01','automated':True,'replace_existing':False,'save':True,'factory':unreal.FbxFactory(),'options':opt})
flag=unreal.SystemLibrary.get_console_variable_bool_value('Interchange.FeatureFlags.Import.FBX')
unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
try:T.import_asset_tasks([task])
finally:unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX '+('1' if flag else '0'))
meshes=[unreal.load_asset(p) for p in task.imported_object_paths];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)]
assert len(meshes)==3,len(meshes)
mat=T.create_asset('M_QuadLines',DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew());assert mat
mat.set_editor_properties({'two_sided':True,'shading_model':unreal.MaterialShadingModel.MSM_UNLIT})
color=M.create_material_expression(mat,unreal.MaterialExpressionVectorParameter,-600,0);color.set_editor_properties({'parameter_name':'LineColor','default_value':unreal.LinearColor(.52,.85,.79,1)})
strength=M.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,-600,200);strength.set_editor_properties({'parameter_name':'LineBrightness','default_value':.8})
mul=M.create_material_expression(mat,unreal.MaterialExpressionMultiply,-300,0)
assert M.connect_material_expressions(color,'RGB',mul,'A');assert M.connect_material_expressions(strength,'',mul,'B');assert M.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
M.recompile_material(mat);E.save_loaded_asset(mat)
mi=T.create_asset('MI_QuadLines_IceTeal',DEST+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());M.set_material_instance_parent(mi,mat);M.update_material_instance(mi);E.save_loaded_asset(mi)
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);rows=[]
credit=(ROOT/'CREDITS.txt').read_text(encoding='utf-8').strip()
for mesh in meshes:
    settings=SM.get_lod_build_settings(mesh,0);settings.set_editor_properties({'recompute_normals':False,'recompute_tangents':False,'use_full_precision_u_vs':True,'use_high_precision_tangent_basis':True,'generate_lightmap_u_vs':False});SM.set_lod_build_settings(mesh,0,settings)
    mesh.set_material(0,mi);E.set_metadata_tag(mesh,'Attribution',credit);E.set_metadata_tag(mesh,'Purpose','Authored surface display quad lines, not original topology');E.save_loaded_asset(mesh)
    actor=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label('YU7_Quad_'+('Hood' if 'Hood' in mesh.get_name() else ('Fender_L' if 'Fender_L' in mesh.get_name() else 'Fender_R')))
    c=actor.static_mesh_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(mesh);c.set_editor_property('cast_shadow',False);c.set_editor_property('receives_decals',False);c.modify();c.set_collision_profile_name('NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    actor.set_actor_transform(hero.get_actor_transform(),False,False);assert actor.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False);actor.set_folder_path('YU7/QuadStudy')
    rows.append({'actor':actor.get_actor_label(),'mesh':mesh.get_path_name(),'bounds':str(mesh.get_bounds())})
# New cameras and sequences avoid modifying or relying on old sequence bindings.
cameras=[]
for name,loc,target,lens in [('Overview',(-780,880,270),(0,0,55),68),('Detail',(-550,430,295),(-125,0,88),65)]:
    camera=A.spawn_actor_from_class(unreal.CineCameraActor,unreal.Vector(*loc));camera.set_actor_label('CAM_YU7_Quad_'+name);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target)),False);camera.set_folder_path('YU7/QuadStudy/Cameras')
    c=camera.get_cine_camera_component();film=c.filmback;film.sensor_width=36;film.sensor_height=20.25;c.filmback=film;c.set_editor_property('current_focal_length',lens);c.set_editor_property('current_aperture',8.)
    focus=c.focus_settings;focus.focus_method=unreal.CameraFocusMethod.DISABLE;c.focus_settings=focus
    seq=T.create_asset('LS_YU7_Quad_'+name,DEST+'/Sequences',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());seq.set_display_rate(unreal.FrameRate(24,1));seq.set_playback_start(0);seq.set_playback_end(24)
    bind=seq.add_possessable(camera);cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(-48,48);cut.set_camera_binding_id(seq.get_binding_id(bind));E.save_loaded_asset(seq)
    cameras.append({'name':name,'sequence':seq.get_path_name(),'camera':camera.get_path_name()})
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'meshes':rows,'cameras':cameras,'material':mi.get_path_name()}
(OUT/'import_v01.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
with (ROOT/'DEV_HISTORY.md').open('a',encoding='utf-8') as f:f.write('\n- v01 三个细线 StaticMesh 已导入独立 /Game/YU7/WireframeStudy/Meshes/v01，使用普通不透明 Unlit 参数材质，不启用原生 wireframe。已附着到副本 YU7_Hero，采用同一变换，关闭碰撞与投影；另建整体与近景相机和原生 Sequencer。保存成功，实际贴合/美术验收待 MRQ 输出。\n')
