"""Audit actual UE render LOD0, not just FBX import options."""
import json
import math
import time
from pathlib import Path
import unreal

ROOT = Path('C:/github2/vehicle_visualization')
OUT = ROOT / 'art/YU7_UNREAL/reports'
DEST = '/Game/Vehicles/YU7_Prepared'
manifest = json.loads((ROOT / 'art/YU7_UNREAL/materials.json').read_text(encoding='utf-8'))
meshes = sorted([unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets(DEST+'/Meshes')], key=lambda m:m.get_name())
meshes = [m for m in meshes if isinstance(m,unreal.StaticMesh)]
assert len(meshes)==121
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name() == '/Game/YU7/Maps/Studio_YU7.Studio_YU7'
sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
q = unreal.GeometryScript_MeshQueries
report = {'engine':unreal.SystemLibrary.get_engine_version(),'world':world.get_path_name(),'mesh_count':len(meshes),'meshes':[],'materials':[],'errors':[],'normal_validation':'All triangle corners of actual render LOD0, including tangents/bitangents; UV0 every triangle. Geometry Script read-only copies.'}
minimum=[float('inf')]*3
maximum=[float('-inf')]*3
credit=(ROOT/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
for mesh_index, mesh in enumerate(meshes):
    settings=sub.get_lod_build_settings(mesh,0)
    # Car paint needs finer tangent quantization than the default 8-bit basis.
    if not settings.get_editor_property('use_high_precision_tangent_basis'):
        settings.set_editor_property('use_high_precision_tangent_basis',True)
        sub.set_lod_build_settings(mesh,0,settings)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    flags={k:settings.get_editor_property(k) for k in ['recompute_normals','recompute_tangents','use_full_precision_u_vs','use_high_precision_tangent_basis','generate_lightmap_u_vs','remove_degenerates']}
    expected=next(r for r in manifest['meshes'] if mesh.get_name().endswith(r['mesh']))
    actual=[s.material_interface.get_name() if s.material_interface else None for s in mesh.get_editor_property('static_materials')]
    row={'name':mesh.get_name(),'triangles':mesh.get_num_triangles(0),'render_vertices':mesh.get_num_vertices(0),'settings':flags,'materials':actual,'material_slots_match':actual==expected['material_slots'],'credit_matches':unreal.EditorAssetLibrary.get_metadata_tag(mesh,'AssetCredit')==credit}
    bb=mesh.get_bounding_box()
    for i,axis in enumerate(['x','y','z']):
        minimum[i]=min(minimum[i],getattr(bb.min,axis)); maximum[i]=max(maximum[i],getattr(bb.max,axis))
    dm,outcome=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,unreal.DynamicMesh(),unreal.GeometryScriptCopyMeshFromAssetOptions(apply_build_settings=True,request_tangents=True),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.RENDER_DATA,lod_index=0))
    assert outcome==unreal.GeometryScriptOutcomePins.SUCCESS
    row.update({'checked_triangles':0,'invalid_normal_tangent_elements':0,'nonfinite_vectors':0,'zero_vectors':0,'max_unit_length_error':0.0,'max_abs_normal_tangent_dot':0.0,'invalid_uv_triangles':0,'zero_area_uv_triangles':0,'uv_channels':q.get_num_uv_sets(dm)})
    for tid in range(q.get_num_triangle_i_ds(dm)):
        if not q.is_valid_triangle_id(dm,tid):
            continue
        _,valid,normal,tangent,bitangent=q.get_triangle_normal_tangents(dm,tid)
        row['checked_triangles']+=1
        if not valid: row['invalid_normal_tangent_elements']+=1
        for corner in ['vector0','vector1','vector2']:
            n=getattr(normal,corner); t=getattr(tangent,corner); b=getattr(bitangent,corner)
            for v in (n,t,b):
                length=math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z)
                if not math.isfinite(length): row['nonfinite_vectors']+=1
                elif length<1e-6: row['zero_vectors']+=1
                else: row['max_unit_length_error']=max(row['max_unit_length_error'],abs(length-1))
            row['max_abs_normal_tangent_dot']=max(row['max_abs_normal_tangent_dot'],abs(n.x*t.x+n.y*t.y+n.z*t.z))
        uv1,uv2,uv3,uvvalid=q.get_triangle_u_vs(dm,0,tid)
        if not uvvalid or not all(math.isfinite(v) for uv in (uv1,uv2,uv3) for v in (uv.x,uv.y)):
            row['invalid_uv_triangles']+=1
        area=abs((uv2.x-uv1.x)*(uv3.y-uv1.y)-(uv2.y-uv1.y)*(uv3.x-uv1.x))
        if area==0: row['zero_area_uv_triangles']+=1
    if not row['material_slots_match'] or not row['credit_matches'] or any(row[k] for k in ['invalid_normal_tangent_elements','nonfinite_vectors','zero_vectors','invalid_uv_triangles']):
        report['errors'].append(row['name'])
    if row['zero_area_uv_triangles']:
        report['errors'].append(row['name'] + ': zero-area UV')
    report['meshes'].append(row)
    if mesh_index%10==0:
        OUT.joinpath('ue_validation_progress.json').write_text(json.dumps({'meshes_done':mesh_index+1,'total':121,'current':mesh.get_name()}),encoding='utf-8')
        unreal.log('YU7 validation: '+str(mesh_index+1)+'/121')
for row in manifest['materials']:
    mat=unreal.load_asset(DEST+'/Materials/'+row['name'])
    assert mat
    tex=unreal.MaterialEditingLibrary.get_material_used_textures(mat)
    expected_tex=sorted(Path(row[k]).stem for k in ['base_texture','normal_texture_dx'] if row[k])
    actual_tex=sorted(t.get_name() for t in tex)
    stats=unreal.MaterialEditingLibrary.get_statistics(mat)
    r={'name':mat.get_name(),'blend_mode':str(mat.get_editor_property('blend_mode')),'shading_model':str(mat.get_editor_property('shading_model')),'textures':actual_tex,'expected_textures':expected_tex,'textures_match':expected_tex==actual_tex,'pixel_shader_instructions':stats.num_pixel_shader_instructions,'expression_count':unreal.MaterialEditingLibrary.get_num_material_expressions(mat)}
    report['materials'].append(r)
    if not r['textures_match']:report['errors'].append(r['name'])
actor=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
report['blueprint_component_count']=len(actor.get_components_by_class(unreal.StaticMeshComponent))
report['actor_scale']=str(actor.get_actor_scale3d())
report['geometry_bounds_min_cm']=minimum;report['geometry_bounds_max_cm']=maximum
report['geometry_dimensions_cm']=[b-a for a,b in zip(minimum,maximum)]
report['render_triangle_count']=sum(m['triangles'] for m in report['meshes'])
report['checked_triangle_count']=sum(m['checked_triangles'] for m in report['meshes'])
report['zero_area_uv_triangle_count']=sum(m['zero_area_uv_triangles'] for m in report['meshes'])
report['max_unit_length_error']=max(m['max_unit_length_error'] for m in report['meshes'])
report['max_abs_normal_tangent_dot']=max(m['max_abs_normal_tangent_dot'] for m in report['meshes'])
report['passed']=not report['errors']
OUT.joinpath('ue_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
RESULT={k:v for k,v in report.items() if k not in ['meshes','materials']}
