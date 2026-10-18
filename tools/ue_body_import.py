"""Import additive full-body quad display geometry into the isolated new map."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_QUAD_BODY/reports'
DEST='/Game/YU7/QuadBodyStudy';E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);M=unreal.MaterialEditingLibrary
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()==DEST+'/Maps/Studio_YU7_QuadBody.Studio_YU7_QuadBody'
VERSION=globals().get('VERSION','v01')
assert not E.does_directory_exist(DEST+'/Meshes/'+VERSION)
opt=unreal.FbxImportUI();opt.set_editor_properties({'automated_import_should_detect_type':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_STATIC_MESH,'import_as_skeletal':False,'import_mesh':True,'import_materials':False,'import_textures':False})
opt.static_mesh_import_data.set_editor_properties({'combine_meshes':False,'auto_generate_collision':False,'generate_lightmap_u_vs':False,'convert_scene':True,'convert_scene_unit':True,'force_front_x_axis':False,'import_uniform_scale':1.,'transform_vertex_to_absolute':True,'build_nanite':False,'normal_import_method':unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS})
task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(ROOT/'art/YU7_QUAD_BODY'/('YU7_BodyLines_'+VERSION+'.fbx')),'destination_path':DEST+'/Meshes/'+VERSION,'automated':True,'replace_existing':False,'save':True,'factory':unreal.FbxFactory(),'options':opt})
flag=unreal.SystemLibrary.get_console_variable_bool_value('Interchange.FeatureFlags.Import.FBX')
unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
try:T.import_asset_tasks([task])
finally:unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX '+('1' if flag else '0'))
meshes=[unreal.load_asset(p) for p in task.imported_object_paths];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)];assert len(meshes)==3
mi=unreal.load_asset(DEST+'/Materials/MI_BodyLines_IceTeal')
if not mi:
    mi=E.duplicate_asset('/Game/YU7/WireframeStudy/Materials/MI_QuadLines_IceTeal',DEST+'/Materials/MI_BodyLines_IceTeal');assert mi
    E.save_loaded_asset(mi)
actors=A.get_all_level_actors();hero=next(a for a in actors if a.get_actor_label()=='YU7_Hero')
for a in actors:
    if a.get_actor_label().startswith('YU7_Quad_'):
        a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.static_mesh_component.set_visibility(False)
SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);rows=[]
for mesh in meshes:
    settings=SM.get_lod_build_settings(mesh,0);settings.set_editor_properties({'recompute_normals':False,'recompute_tangents':False,'use_full_precision_u_vs':True,'use_high_precision_tangent_basis':True,'generate_lightmap_u_vs':False});SM.set_lod_build_settings(mesh,0,settings)
    mesh.set_material(0,mi);E.set_metadata_tag(mesh,'Attribution',(ROOT/'CREDITS.txt').read_text(encoding='utf-8').strip());E.set_metadata_tag(mesh,'Purpose','Authored continuous exterior quad display, not recovered topology');E.save_loaded_asset(mesh)
    group='Mirror_L' if 'Mirror_L' in mesh.get_name() else ('Mirror_R' if 'Mirror_R' in mesh.get_name() else 'Body')
    label='YU7_BodyQuad_'+group;found=[a for a in actors if a.get_actor_label()==label];assert len(found)<=1
    actor=found[0] if found else A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());actor.set_actor_label(label)
    c=actor.static_mesh_component;c.modify();c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(mesh);c.set_editor_property('cast_shadow',False);c.set_editor_property('receives_decals',False);c.set_collision_profile_name('NoCollision')
    actor.set_actor_transform(hero.get_actor_transform(),False,False);assert actor.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False);actor.set_folder_path('YU7/BodyQuad')
    rows.append({'actor':label,'mesh':mesh.get_path_name(),'triangles':mesh.get_num_triangles(0)})
cameras=[]
for name,loc,target,lens in [('Overview',(-780,880,270),(0,0,55),68),('Detail',(-550,430,295),(-125,0,88),65),('Rear',(780,880,275),(0,0,62),68)]:
    path=DEST+'/Sequences/LS_YU7_BodyQuad_'+name
    if E.does_asset_exist(path):continue
    camera=A.spawn_actor_from_class(unreal.CineCameraActor,unreal.Vector(*loc));camera.set_actor_label('CAM_YU7_BodyQuad_'+name);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target)),False);camera.set_folder_path('YU7/BodyQuad/Cameras')
    c=camera.get_cine_camera_component();film=c.filmback;film.sensor_width=36;film.sensor_height=20.25;c.filmback=film;c.set_editor_property('current_focal_length',lens);c.set_editor_property('current_aperture',8.)
    focus=c.focus_settings;focus.focus_method=unreal.CameraFocusMethod.DISABLE;c.focus_settings=focus
    seq=T.create_asset('LS_YU7_BodyQuad_'+name,DEST+'/Sequences',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());seq.set_display_rate(unreal.FrameRate(24,1));seq.set_playback_start(0);seq.set_playback_end(24)
    bind=seq.add_possessable(camera);cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(-48,48);cut.set_camera_binding_id(seq.get_binding_id(bind));E.save_loaded_asset(seq)
    cameras.append({'name':name,'sequence':seq.get_path_name()})
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'meshes':rows,'cameras':cameras,'material':mi.get_path_name()}
(OUT/('import_'+VERSION+'.json')).write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
