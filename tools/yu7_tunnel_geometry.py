"""Offline deterministic display geometry. Original vehicle and v03 lines stay intact."""
import bpy,json,math,time
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/prepared';O.mkdir(parents=True,exist_ok=True)
assert not (O/'YU7_TunnelEffects_v01.fbx').exists()
assert 'YU7_BodyStudy_v03' in bpy.data.filepath
col=bpy.data.collections.new('YU7_TUNNEL_EFFECTS_v01');bpy.context.scene.collection.children.link(col)
originals=sorted([o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SM_YU7_')],key=lambda o:o.name);assert len(originals)==121
vs=[];fs=[];allowed=[]
for o in originals:
    base=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
    for p in o.data.polygons:
        fs.append([base+i for i in p.vertices]);m=o.data.materials[p.material_index] if len(o.data.materials)>p.material_index else None;allowed.append(bool(m and 'CarPaint' in m.name))
tree=BVHTree.FromPolygons(vs,fs)
objects=[];report={'source_objects':len(originals),'grid':[],'paths':[]}
for old in bpy.data.collections['YU7_BODY_QUAD_v03'].objects:
    if old.type!='MESH':continue
    o=old.copy();o.data=old.data.copy();o.name=old.name.replace('SM_BodyLines','SM_TunnelGrid');col.objects.link(o)
    uv=o.data.uv_layers[0]
    for l in o.data.loops:uv.data[l.index].uv=((2.5-o.data.vertices[l.vertex_index].co.x)/5.,0.)
    objects.append(o);report['grid'].append({'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'same_positions_as':old.name})

def make_tubes(name,paths,width,world=False):
    vv=[];ff=[];uu=[]
    for lane,points in paths:
        if len(points)<2:continue
        base=len(vv)
        for i,(p,n) in enumerate(points):
            tangent=(points[min(i+1,len(points)-1)][0]-points[max(0,i-1)][0]).normalized()
            n=(n-tangent*n.dot(tangent)).normalized();side=tangent.cross(n).normalized()
            for j in range(6):
                q=p+(n*math.cos(j*math.tau/6)+side*math.sin(j*math.tau/6))*width*.5
                vv.append(tuple(q));uu.append(((2.4-p.x)/15 if world else (2.5-p.x)/5,lane))
        for k in range(len(points)-1):
            for j in range(6):a=base+6*k+j;b=base+6*k+(j+1)%6;ff.append((a,b,b+6,a+6))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vv,[],ff);mesh.update();uv=mesh.uv_layers.new(name='FlowCoordinate')
    for p in mesh.polygons:
        p.use_smooth=True
        for li in p.loop_indices:uv.data[li].uv=uu[mesh.loops[li].vertex_index]
    o=bpy.data.objects.new(name,mesh);col.objects.link(o);objects.append(o)
    return o

paths=[]
for sign in [-1,1]:
    for lane in range(3):
        current=[];length=0;parts=0
        for k in range(1201):
            x=2.4-k*4.8/1200
            if lane==0:
                z=.91+.08*math.sin((2.4-x)*.7);origin=Vector((x,sign*3,z));direction=Vector((0,-sign,0))
            elif lane==1:
                z=.56+.47*math.exp(-((x-1.51)/.62)**2)+.47*math.exp(-((x+1.483)/.63)**2)
                origin=Vector((x,sign*3,z));direction=Vector((0,-sign,0))
            else:
                if x<.72:break
                origin=Vector((x,sign*(.32+(2.4-x)*.18),3));direction=Vector((0,0,-1))
            p,n,idx,d=tree.ray_cast(origin,direction,6)
            good=p is not None and allowed[idx] and n.dot(-direction)>.12
            if good:p=p+n*.004
            if (not good) or (current and (current[-1][0]-p).length>.025):
                if len(current)>2:paths.append((lane*.12,current));parts+=1;length+=sum((a[0]-b[0]).length for a,b in zip(current,current[1:]))
                current=[]
            if good:current.append((p,n))
        if len(current)>2:paths.append((lane*.12,current));parts+=1;length+=sum((a[0]-b[0]).length for a,b in zip(current,current[1:]))
        report['paths'].append({'side':sign,'lane':lane,'segments':parts,'length_m':length})
make_tubes('SM_TunnelSurfaceFlow_v01',paths,.0036)
# World-space emission coordinates: a point's U is the instant the moving
# rear of the car passed it. Shader age = sequence time - U, no sim history.
wake=[]
for sign in [-1,1]:
    for j in range(7):
        pts=[]
        for k in range(1601):
            x=35-k*.15;y=sign*(.66+j*.052+.022*math.sin(x*1.7+j*.8));z=.72+j*.065+.025*math.sin(x*1.1+j*1.2)
            pts.append((Vector((x,y,z)),Vector((0,0,1))))
        wake.append((j/7,pts))
make_tubes('SM_TunnelWorldWake_v01',wake,.0045,True)
for c in bpy.data.collections:
    if c.name.startswith(('YU7_BODY_QUAD_','YU7_QUAD_STUDY_')):c.hide_viewport=True;c.hide_render=True
for o in bpy.context.selected_objects:o.select_set(False)
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(O/'YU7_TunnelEffects_v01.fbx'),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_space_transform=True,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,use_triangles=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'YU7_TunnelEffects_v01.blend'),check_existing=False)
report['outputs']=[{'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in objects]
(R/'art/YU7_TUNNEL_FLOW/reports/geometry_v01.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
