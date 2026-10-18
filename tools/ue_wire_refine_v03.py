"""Swap only study actors to v03, preserving previous meshes and originals."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports';DEST='/Game/YU7/WireframeStudy'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()==DEST+'/Maps/Studio_YU7_QuadStudy.Studio_YU7_QuadStudy'
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert not E.does_directory_exist(DEST+'/Meshes/v03')
opt=unreal.FbxImportUI();opt.set_editor_properties({'automated_import_should_detect_type':False,'mesh_type_to_import':unreal.FBXImportType.FBXIT_STATIC_MESH,'import_as_skeletal':False,'import_mesh':True,'import_materials':False,'import_textures':False})
opt.static_mesh_import_data.set_editor_properties({'combine_meshes':False,'auto_generate_collision':False,'generate_lightmap_u_vs':False,'convert_scene':True,'convert_scene_unit':True,'force_front_x_axis':False,'import_uniform_scale':1.,'transform_vertex_to_absolute':True,'build_nanite':False,'normal_import_method':unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS})
task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(ROOT/'art/YU7_WIREFRAME/YU7_QuadLines_v03.fbx'),'destination_path':DEST+'/Meshes/v03','automated':True,'replace_existing':False,'save':True,'factory':unreal.FbxFactory(),'options':opt})
flag=unreal.SystemLibrary.get_console_variable_bool_value('Interchange.FeatureFlags.Import.FBX');unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX 0')
try:T.import_asset_tasks([task])
finally:unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX '+('1' if flag else '0'))
meshes=[unreal.load_asset(p) for p in task.imported_object_paths];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)];assert len(meshes)==3
mi=unreal.load_asset(DEST+'/Materials/MI_QuadLines_IceTeal');M.set_material_instance_scalar_parameter_value(mi,'LineBrightness',100.);M.update_material_instance(mi);E.save_loaded_asset(mi)
SM=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);rows=[]
for mesh in meshes:
    settings=SM.get_lod_build_settings(mesh,0);settings.set_editor_properties({'recompute_normals':False,'recompute_tangents':False,'use_full_precision_u_vs':True,'use_high_precision_tangent_basis':True,'generate_lightmap_u_vs':False});SM.set_lod_build_settings(mesh,0,settings)
    mesh.set_material(0,mi);E.set_metadata_tag(mesh,'Attribution',(ROOT/'CREDITS.txt').read_text(encoding='utf-8').strip());E.save_loaded_asset(mesh)
    group='Hood' if 'Hood' in mesh.get_name() else ('Fender_L' if 'Fender_L' in mesh.get_name() else 'Fender_R')
    actor=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Quad_'+group);actor.modify();actor.static_mesh_component.set_static_mesh(mesh);rows.append([group,mesh.get_path_name()])
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'swapped':rows,'brightness':100.}
(OUT/'refine_v03.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
