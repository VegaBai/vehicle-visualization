import bpy, bmesh, math, json, re
import numpy as np
from pathlib import Path
from mathutils import Vector

OUT=Path(r'C:\github2\vehicle_visualization\art\YU7_UNREAL')
audit=json.loads((OUT/'reports/geometry_audit.json').read_text())
lookup={d['name']:d for d in audit['objects']}
scene=bpy.context.scene
meshes=[o for o in scene.objects if o.type=='MESH']
changes=[]
for o in meshes:
    d=lookup[o.name]; m=o.data
    change={'source_name':o.name,'removed_degenerate_faces':0,'rewound_faces':0,'generated_uv':False,'uv_triangles_repaired':0}
    if d['degenerate_faces'] or d['inconsistent_edges']:
        old_normals={p.index:{m.loops[i].vertex_index:m.corner_normals[i].vector.copy() for i in p.loop_indices} for p in m.polygons}
        old_winding={p.index:tuple(p.vertices) for p in m.polygons}
        bm=bmesh.new();bm.from_mesh(m);bm.faces.ensure_lookup_table();bm.verts.ensure_lookup_table()
        layer=bm.faces.layers.int.new('_yu7_source_face')
        for f in bm.faces:f[layer]=f.index
        bad=[f for f in bm.faces if f.calc_area()<1e-14]
        change['removed_degenerate_faces']=len(bad)
        if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
        if d['inconsistent_edges']:bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.normal_update()
        recovered=[]
        for f in bm.faces:
            src=f[layer]
            old=old_winding[src]
            new=tuple(v.index for v in f.verts)
            if new not in [old[i:]+old[:i] for i in range(len(old))]:change['rewound_faces']+=1
            for loop in f.loops:
                n=old_normals[src][loop.vert.index]
                if n.dot(f.normal)<-0.05:n=-n
                recovered.append(tuple(n))
        bm.faces.layers.int.remove(layer)
        bm.to_mesh(m);bm.free();m.update()
        m.normals_split_custom_set(recovered)
    if not m.uv_layers:
        o['generated_uv_requires_solid_material']=True
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
        m.uv_layers.new(name='UV0')
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015,correct_aspect=True,scale_to_bounds=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        change['generated_uv']=True
    m.uv_layers[0].name='UV0';m.uv_layers.active_index=0
    m.uv_layers[0].active_render=True
    m.calc_loop_triangles()
    uv=m.uv_layers[0].data
    delta=1/32768
    for t in m.loop_triangles:
        ids=list(t.loops);p=[uv[i].uv.copy() for i in ids]
        a=p[1]-p[0];b=p[2]-p[0]
        if abs(a.x*b.y-a.y*b.x)/2>=1e-14:continue
        assert len(m.polygons[t.polygon_index].vertices)==3, 'UV repair expects source triangulation'
        pairs=[(0,1,2),(1,2,0),(2,0,1)]
        i,j,k=max(pairs,key=lambda t:(p[t[1]]-p[t[0]]).length_squared)
        edge=p[j]-p[i]
        if edge.length<delta:
            center=(p[0]+p[1]+p[2])/3
            p=[center+Vector((-delta/2,-delta/2)),center+Vector((delta/2,-delta/2)),center+Vector((-delta/2,delta/2))]
        else:
            perp=Vector((-edge.y,edge.x)).normalized()*delta
            p[k]+=perp
        for loop_id,value in zip(ids,p):uv[loop_id].uv=value
        change['uv_triangles_repaired']+=1
    m.update()
    m.calc_tangents(uvmap='UV0')
    tangents=np.empty((len(m.loops),3),dtype=np.float32);m.loops.foreach_get('tangent',tangents.ravel())
    change['invalid_tangents']=int(np.count_nonzero(~np.isfinite(tangents).all(axis=1)|(np.linalg.norm(tangents,axis=1)<.9)))
    short=o.name.split(':')[-1].split('_car')[0]
    o.name='SM_YU7_'+str(len(changes)+1).zfill(3)+'_'+re.sub('[^A-Za-z0-9_]','_',short)
    m.name=o.name+'_Mesh'
    change['export_name']=o.name
    changes.append(change)
dashboard=bpy.data.objects['SM_YU7_052_carInternal_Dashboard']
dm=dashboard.data
dm.calc_tangents(uvmap='UV0')
if any(l.tangent.length<.9 for l in dm.loops):
    dm.vertices[545].co.x+=0.0001
    dm.free_tangents();dm.update();dm.calc_tangents(uvmap='UV0')
    dashboard['tangent_repair']='Vertex 545 shifted +X 0.1 mm to resolve a numerically singular sliver corner.'
    for c in changes:
        if c['export_name']==dashboard.name:
            c['dashboard_vertex_shift_mm']=0.1
            c['invalid_tangents']=sum(l.tangent.length<.9 for l in dm.loops)
scene['yu7_geometry_prepared']=True
(OUT/'reports/geometry_repairs.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print(json.dumps({'meshes':len(changes),'removed_degenerate_faces':sum(c['removed_degenerate_faces'] for c in changes),'rewound_faces':sum(c['rewound_faces'] for c in changes),'generated_uv_objects':sum(c['generated_uv'] for c in changes),'repaired_degenerate_uv_triangles':sum(c['uv_triangles_repaired'] for c in changes),'invalid_tangents':sum(c['invalid_tangents'] for c in changes)},indent=2))
