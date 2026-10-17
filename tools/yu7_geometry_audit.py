import bpy, bmesh, json, math
import numpy as np
from pathlib import Path
from mathutils import Matrix, Vector

OUT = Path(r"C:\github2\vehicle_visualization\art\YU7_UNREAL")
scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == 'MESH']
all_points=[]
for o in meshes:
    a=np.empty((len(o.data.vertices),3),dtype=np.float64)
    o.data.vertices.foreach_get('co',a.ravel())
    w=np.array(o.matrix_world)
    all_points.append(a @ w[:3,:3].T + w[:3,3])
points=np.concatenate(all_points)
lo,hi=points.min(axis=0),points.max(axis=0)
factor=4.999/(hi[1]-lo[1])
center=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
transform=Matrix.Rotation(math.pi/2,4,'Z') @ Matrix.Scale(factor,4) @ Matrix.Translation(-center)
world={o:o.matrix_world.copy() for o in meshes}
changes=[]
for o in meshes:
    m=o.data.copy()
    o.data=m
    xform=transform @ world[o]
    assert xform.determinant()>0, 'Unexpected mirrored transform: '+o.name
    normals=np.empty((len(m.corner_normals),3),dtype=np.float32)
    m.corner_normals.foreach_get('vector',normals.ravel())
    nmat=np.array(xform.to_3x3().inverted().transposed())
    normals=normals @ nmat.T
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-15)
    m.transform(xform)
    o.parent=None
    o.matrix_world=Matrix.Identity(4)
    m.normals_split_custom_set(normals.tolist())
    o['source_object_name']=o.name
    o['source_asset']='2025 Xiaomi YU7 - Ddiaz Design'
    m.update()
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1.0
bpy.context.view_layer.update()

audit=[]
for o in meshes:
    m=o.data
    bm=bmesh.new(); bm.from_mesh(m); bm.normal_update()
    components=[]; seen=set()
    for f in bm.faces:
        if f in seen: continue
        stack=[f]; seen.add(f); group=[]
        while stack:
            f2=stack.pop(); group.append(f2)
            for e in f2.edges:
                for f3 in e.link_faces:
                    if f3 not in seen: seen.add(f3); stack.append(f3)
        edges=set(e for f2 in group for e in f2.edges)
        closed=all(e.is_manifold for e in edges)
        vol=sum(f2.calc_center_median().dot(f2.normal)*f2.calc_area()/3 for f2 in group) if closed else None
        components.append({'faces':len(group),'closed':closed,'volume':vol})
    d={'name':o.name,'triangles':len(m.polygons),'dimensions':list(o.dimensions),'center':list(sum((Vector(c) for c in o.bound_box),Vector())/8),'materials':[x.name for x in m.materials], 'degenerate_faces':sum(f.calc_area()<1e-14 for f in bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_junctions':sum(len(e.link_faces)>2 for e in bm.edges),'inconsistent_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'components':components,'invalid_normal_vectors':0}
    cn=np.empty((len(m.corner_normals),3),dtype=np.float32); m.corner_normals.foreach_get('vector',cn.ravel())
    d['invalid_normal_vectors']=int(np.count_nonzero(~np.isfinite(cn).all(axis=1) | (np.linalg.norm(cn,axis=1)<0.9)))
    d['uv_layers']=[]
    m.calc_loop_triangles()
    loops=np.empty((len(m.loop_triangles),3),dtype=np.int32);m.loop_triangles.foreach_get('loops',loops.ravel())
    for layer in m.uv_layers:
        u=np.empty((len(layer.data),2),dtype=np.float32); layer.data.foreach_get('uv',u.ravel())
        tri=u[loops]; a=tri[:,1]-tri[:,0];b=tri[:,2]-tri[:,0]; area=np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])/2
        d['uv_layers'].append({'name':layer.name,'invalid_coords':int(np.count_nonzero(~np.isfinite(u))),'degenerate_triangles':int(np.count_nonzero(area<1e-14)),'min':u.min(axis=0).tolist(),'max':u.max(axis=0).tolist()})
    audit.append(d);bm.free()
report={'scale_factor':factor,'target_length_m':4.999,'source_bounds':[lo.tolist(),hi.tolist()],'transform':[list(row) for row in transform],'front_axis':'+X','up_axis':'+Z','origin':'ground center of overall bounds','objects':audit}
(OUT/'reports/geometry_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
summary={'scale_factor':factor,'problems':[{'name':d['name'],'degenerate_faces':d['degenerate_faces'],'inconsistent_edges':d['inconsistent_edges'],'invalid_normal_vectors':d['invalid_normal_vectors'],'negative_closed_components':sum(c['closed'] and c['volume'] < -1e-12 for c in d['components']),'uv':d['uv_layers']} for d in audit if d['degenerate_faces'] or d['inconsistent_edges'] or any(c['closed'] and c['volume'] < -1e-12 for c in d['components']) or not d['uv_layers'] or any(u['degenerate_triangles'] for u in d['uv_layers'])], 'paint_parts':[{'name':d['name'],'center':d['center'],'dimensions':d['dimensions'],'materials':d['materials']} for d in audit if 'carPaint' in d['name']]}
print(json.dumps(summary,indent=2))
