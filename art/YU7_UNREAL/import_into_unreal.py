"""UE5 editor import helper. Execution results are recorded in reports/ue_jobs.

Run with Tools > Execute Python Script after enabling Python Editor Script Plugin.
Creates assets in a new content folder; does not edit or save the current level.
Uses the legacy FbxFactory and conventional UE material expressions.
"""
import json
from pathlib import Path
import unreal

SOURCE = Path(__file__).resolve().parent
DESTINATION = '/Game/Vehicles/YU7_Prepared'


def run(resume=False):
    manifest = json.loads((SOURCE / 'materials.json').read_text(encoding='utf-8'))
    if unreal.EditorAssetLibrary.does_directory_exist(DESTINATION) and not resume:
        raise RuntimeError('Destination already exists. Choose a new DESTINATION; no existing assets were changed.')
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    edit = unreal.MaterialEditingLibrary
    texture_names = sorted({r[k] for r in manifest['materials'] for k in ['base_texture', 'normal_texture_dx'] if r[k]})
    textures = {}
    data_textures = {r['base_texture'] for r in manifest['materials'] if r['base_texture_data']}
    normal_textures = {r['normal_texture_dx'] for r in manifest['materials'] if r['normal_texture_dx']}
    for filename in texture_names:
        existing = unreal.load_asset(DESTINATION + '/Textures/' + Path(filename).stem) if resume else None
        if existing:
            textures[filename] = existing
            continue
        task = unreal.AssetImportTask()
        task.filename = str(SOURCE / 'Textures' / filename)
        task.destination_path = DESTINATION + '/Textures'
        task.automated = True
        task.replace_existing = False
        task.save = True
        tools.import_asset_tasks([task])
        assets = [unreal.load_asset(p) for p in task.imported_object_paths]
        asset = next((a for a in assets if isinstance(a, unreal.Texture2D)), None)
        if asset is None:
            raise RuntimeError('Texture import failed: ' + filename)
        asset.set_editor_property('srgb', filename not in data_textures | normal_textures)
        if filename in normal_textures:
            asset.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
            asset.set_editor_property('flip_green_channel', False)  # Already DirectX -Y.
        unreal.EditorAssetLibrary.save_loaded_asset(asset)
        textures[filename] = asset

    materials = {}
    for row in manifest['materials']:
        material = unreal.load_asset(DESTINATION + '/Materials/' + row['name']) if resume else None
        if material:
            edit.delete_all_material_expressions(material)
        else:
            material = tools.create_asset(row['name'], DESTINATION + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
        if not material:
            raise RuntimeError('Material creation failed: ' + row['name'])

        attrs = None
        if row['clear_coat']:
            material.set_editor_property('use_material_attributes', True)
            attrs = edit.create_material_expression(material, unreal.MaterialExpressionMakeMaterialAttributes, 0, 0)
            assert edit.connect_material_property(attrs, '', unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
        def connect(node, output, prop):
            if attrs:
                names = {unreal.MaterialProperty.MP_BASE_COLOR: 'basecolor', unreal.MaterialProperty.MP_METALLIC: 'metallic', unreal.MaterialProperty.MP_ROUGHNESS: 'roughness', unreal.MaterialProperty.MP_NORMAL: 'normal'}
                want = names.get(prop, prop)
                inputs = edit.get_material_expression_input_names(attrs)
                pin = next((p for p in inputs if p.lower().replace(' ', '').replace('_', '') == want), None)
                if not pin:
                    raise RuntimeError('Missing material attribute pin: ' + str(want) + ' / ' + str(inputs))
                return edit.connect_material_expressions(node, output, attrs, pin)
            return edit.connect_material_property(node, output, prop)

        def scalar(value, prop, y):
            node = edit.create_material_expression(material, unreal.MaterialExpressionConstant, -300, y)
            node.set_editor_property('r', float(value))
            if not connect(node, '', prop):
                raise RuntimeError('Material scalar connection failed: ' + str(prop))
            return node

        def vector(color, y):
            node = edit.create_material_expression(material, unreal.MaterialExpressionConstant3Vector, -700, y)
            node.set_editor_property('constant', unreal.LinearColor(*color, 1.0))
            return node

        def sample(filename, normal=False, data=False, y=0):
            node = edit.create_material_expression(material, unreal.MaterialExpressionTextureSample, -900, y)
            node.set_editor_property('texture', textures[filename])
            node.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if normal else unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR if data else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
            return node

        color = row['ue_glass_color_linear'] if row['blend_mode'] == 'TRANSLUCENT' else row['base_color_linear']
        factor = vector(color, 0)
        base = factor
        if row['base_texture']:
            tex = sample(row['base_texture'], data=row['base_texture_data'])
            multiply = edit.create_material_expression(material, unreal.MaterialExpressionMultiply, -400, 0)
            edit.connect_material_expressions(tex, 'RGB', multiply, 'A')
            edit.connect_material_expressions(factor, '', multiply, 'B')
            base = multiply
            if row['blend_mode'] == 'MASKED':
                material.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
                edit.connect_material_property(tex, 'A', unreal.MaterialProperty.MP_OPACITY_MASK)
        assert connect(base, '', unreal.MaterialProperty.MP_BASE_COLOR)
        scalar(row['metallic'], unreal.MaterialProperty.MP_METALLIC, 180)
        scalar(row['roughness'], unreal.MaterialProperty.MP_ROUGHNESS, 260)
        if row['clear_coat']:
            material.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_CLEAR_COAT)
            scalar(row['clear_coat'], 'clearcoat', 340)
            scalar(row['clear_coat_roughness'], 'clearcoatroughness', 420)
        if row['normal_texture_dx']:
            normal = sample(row['normal_texture_dx'], normal=True, y=550)
            assert connect(normal, 'RGB', unreal.MaterialProperty.MP_NORMAL)
        if row['blend_mode'] == 'TRANSLUCENT':
            material.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
            material.set_editor_property('two_sided', True)
            material.set_editor_property('translucency_lighting_mode', unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
            scalar(row['opacity'], unreal.MaterialProperty.MP_OPACITY, 500)
        edit.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        materials[row['name']] = material

    options = unreal.FbxImportUI()
    options.set_editor_property('automated_import_should_detect_type', False)
    options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)
    options.set_editor_property('import_as_skeletal', False)
    options.set_editor_property('import_mesh', True)
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    data = options.static_mesh_import_data
    for key, value in {
        'combine_meshes': False,
        'auto_generate_collision': False,
        'generate_lightmap_u_vs': False,
        'convert_scene': True,
        'convert_scene_unit': True,
        'force_front_x_axis': False,
        'import_uniform_scale': 1.0,
        'transform_vertex_to_absolute': True,
        'bake_pivot_in_vertex': False,
        'build_nanite': False,
        'normal_import_method': unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS,
    }.items():
        data.set_editor_property(key, value)
    task = unreal.AssetImportTask()
    task.filename = str(SOURCE / 'YU7_Unreal.fbx')
    task.destination_path = DESTINATION + '/Meshes'
    task.automated = True
    task.replace_existing = False
    task.save = True
    task.factory = unreal.FbxFactory()
    task.options = options
    tools.import_asset_tasks([task])
    meshes = [a for p in task.imported_object_paths if isinstance((a := unreal.load_asset(p)), unreal.StaticMesh)]
    if len(meshes) != len(manifest['meshes']):
        raise RuntimeError(f'Expected 121 separate meshes, received {len(meshes)}. Check the active FBX importer.')
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    credit = (SOURCE / 'CREDITS.txt').read_text(encoding='utf-8').strip()
    for mesh in meshes:
        names = [r for r in manifest['meshes'] if mesh.get_name().endswith(r['mesh'])]
        expected = names[0]['material_slots'] if len(names) == 1 else None
        for index, slot in enumerate(mesh.get_editor_property('static_materials')):
            key = str(slot.get_editor_property('imported_material_slot_name'))
            if key not in materials and expected and index < len(expected):
                key = expected[index]
            if key not in materials:
                raise RuntimeError(f'Unresolved material slot: {mesh.get_name()} / {key}')
            mesh.set_material(index, materials[key])
        settings = subsystem.get_lod_build_settings(mesh, 0)
        for key, value in {'recompute_normals': False, 'recompute_tangents': False, 'use_full_precision_u_vs': True, 'use_high_precision_tangent_basis': True, 'generate_lightmap_u_vs': False}.items():
            settings.set_editor_property(key, value)
        subsystem.set_lod_build_settings(mesh, 0, settings)
        unreal.EditorAssetLibrary.set_metadata_tag(mesh, 'AssetCredit', credit)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    unreal.log(f'YU7 imported: {len(meshes)} meshes, {len(materials)} materials. Assets: {DESTINATION}')
    unreal.log('All mesh pivots share the ground origin. Place all parts at the same transform. Final visible Credits still need to be created in the project.')


if __name__ == '__main__':
    run()
