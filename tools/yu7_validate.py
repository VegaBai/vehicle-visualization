import bpy,bmesh,json,hashlib,re
import numpy as np
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\github2\vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL'
scene=bpy.data.scenes['YU7_PREP'];bpy.context.window.scene=scene
original=list(bpy.data.collections['YU7_VEHICLE'].objects)

def stats(objects,topology=False):
    result=[];points=[]
    for o in objects:
        m=o.data;m.calc_loop_triangles()
        a=np.empty((len(m.vertices),3),dtype=np.float64);m.vertices.foreach_get('co',a.ravel())
        w=np.array(o.matrix_world);points.append(a@w[:3,:3].T+w[:3,3])
        n=np.empty((len(m.corner_normals),3),dtype=np.float32);m.corner_normals.foreach_get('vector',n.ravel())
        loops=np.empty((len(m.loop_triangles),3),dtype=np.int32);m.loop_triangles.foreach_get('loops',loops.ravel())
        uv=np.empty((len(m.uv_layers[0].data),2),dtype=np.float32);m.uv_layers[0].data.foreach_get('uv',uv.ravel())
        t=uv[loops];a=t[:,1]-t[:,0];b=t[:,2]-t[:,0];uvarea=np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])/2
        m.calc_tangents(uvmap=m.uv_layers[0].name)
        tan=np.empty((len(m.loops),3),dtype=np.float32);m.loops.foreach_get('tangent',tan.ravel())
        d={'name':o.name,'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'uv_channels':len(m.uv_layers),'bad_uv_triangles':int(np.count_nonzero(uvarea<1e-14)),'invalid_uv_values':int(np.count_nonzero(~np.isfinite(uv))),'custom_normals':m.has_custom_normals,'invalid_normals':int(np.count_nonzero(~np.isfinite(n).all(axis=1)|(np.linalg.norm(n,axis=1)<.9))),'invalid_tangents':int(np.count_nonzero(~np.isfinite(tan).all(axis=1)|(np.linalg.norm(tan,axis=1)<.9))),'material_slots':[s.material.name if s.material else None for s in o.material_slots]}
        if topology:
            bm=bmesh.new();bm.from_mesh(m)
            d['inconsistent_edges']=sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
            d['degenerate_faces']=sum(f.calc_area()<1e-14 for f in bm.faces)
            d['boundary_edges']=sum(e.is_boundary for e in bm.edges)
            bm.free()
        result.append(d)
    xyz=np.concatenate(points);lo=xyz.min(axis=0);hi=xyz.max(axis=0)
    return {'objects':result,'bounds_min':lo.tolist(),'bounds_max':hi.tolist(),'dimensions':(hi-lo).tolist(),'totals':{k:sum(d[k] for d in result) for k in ['vertices','triangles','bad_uv_triangles','invalid_uv_values','invalid_normals','invalid_tangents']}}

before=stats(original,True)
check=bpy.data.scenes.new('YU7_FBX_ROUNDTRIP');check.unit_settings.system='METRIC';check.unit_settings.scale_length=1.
bpy.context.window.scene=check
bpy.ops.import_scene.fbx(filepath=str(OUT/'YU7_Unreal.fbx'),use_custom_normals=True,use_image_search=True)
imported=[o for o in check.objects if o.type=='MESH'];after=stats(imported,True)
comparisons=[]
for a,b in zip(sorted(original,key=lambda o:o.name),sorted(imported,key=lambda o:o.name)):
    def pos(o):
        arr=np.empty((len(o.data.vertices),3),dtype=np.float64);o.data.vertices.foreach_get('co',arr.ravel());w=np.array(o.matrix_world);return arr@w[:3,:3].T+w[:3,3]
    pa,pb=pos(a),pos(b)
    def normals(o):
        ns=np.empty((len(o.data.corner_normals),3),dtype=np.float64);o.data.corner_normals.foreach_get('vector',ns.ravel());nm=np.array(o.matrix_world.to_3x3().inverted().transposed());ns=ns@nm.T;return ns/np.maximum(np.linalg.norm(ns,axis=1,keepdims=True),1e-15)
    na,nb=normals(a),normals(b)
    dots=np.sum(na*nb,axis=1)
    source_slots=[s.material.name for s in a.material_slots]
    imported_slots=[re.sub(r'\.\d{3}$','',s.material.name) for s in b.material_slots]
    comparisons.append({'source':a.name,'imported':b.name,'same_vertex_count':len(pa)==len(pb),'max_vertex_error_m':float(np.max(np.linalg.norm(pa-pb,axis=1))) if pa.shape==pb.shape else None,'same_material_slot_count':len(a.material_slots)==len(b.material_slots),'material_names_and_order_match':source_slots==imported_slots,'max_corner_normal_error_degrees':float(np.degrees(np.arccos(np.clip(dots,-1,1))).max())})
src_manifest=json.loads((OUT/'reports/source_manifest.json').read_text())
unchanged=all(hashlib.sha256((ROOT/'art/FINAL_MODEL'/name).read_bytes()).hexdigest()==v['sha256'] for name,v in src_manifest.items())
referenced={n.image for o in original for s in o.material_slots if s.material for n in s.material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
missing=[i.name for i in referenced if not Path(bpy.path.abspath(i.filepath)).is_file()]
report={'prepared':before,'reimported':after,'comparisons':comparisons,'source_files_unchanged':unchanged,'missing_textures':missing,'unreal_engine_import_tested':False,'lightmap_uv_channel_created':False,'notes':['Original material UV overlaps/mirroring retained. UV0 is not a unique lightmap atlas.','Two material fallbacks cover source faces with missing UVs; original atlas mapping could not be recovered.','One dashboard vertex moved 0.1 mm to resolve a numerically singular tangent corner.']}
report['passed']=bool(unchanged and not missing and len(original)==len(imported)==121 and before['totals']['triangles']==after['totals']['triangles'] and all(before['totals'][k]==after['totals'][k]==0 for k in ['bad_uv_triangles','invalid_uv_values','invalid_normals','invalid_tangents']) and all(c['same_vertex_count'] and c['same_material_slot_count'] and c['max_vertex_error_m']<1e-5 for c in comparisons) and sum(o['inconsistent_edges']+o['degenerate_faces'] for o in before['objects'])==0)
report['passed']=report['passed'] and all(c['material_names_and_order_match'] and c['max_corner_normal_error_degrees']<1.0 for c in comparisons)
(OUT/'reports/final_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.context.window.scene=scene
for o in list(check.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.scenes.remove(check)
bpy.data.orphans_purge(do_recursive=True)
# Preserve the source scene and its inspection studio, without the roundtrip copy.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'YU7_Prepared.blend'),check_existing=False)
print(json.dumps({'passed':report['passed'],'source_files_unchanged':unchanged,'dimensions_m':before['dimensions'],'meshes':len(original),'triangles':before['totals']['triangles'],'before':before['totals'],'after':after['totals'],'max_roundtrip_vertex_error_m':max(c['max_vertex_error_m'] or 0 for c in comparisons),'missing_textures':missing},indent=2))
