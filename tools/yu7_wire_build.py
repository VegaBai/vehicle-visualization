"""Offline, additive surface-line geometry. Execute in prepared Blender scene.

Two authored parameter fields form quad-looking cells: bonnet flow coordinates
and wheel-centred fender coordinates. Display topology, not source topology.
"""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME'
VERSION='v03';dest=OUT/('YU7_QuadLines_'+VERSION+'.fbx')
assert not dest.exists(), 'Use a new version; never overwrite prepared sources'
original_path=bpy.data.filepath
assert 'YU7_Prepared.blend' in original_path or 'YU7_QuadStudy_' in original_path
col=bpy.data.collections.new('YU7_QUAD_STUDY_'+VERSION);bpy.context.scene.collection.children.link(col)
names=['SM_YU7_040_carPaint_2_1_','SM_YU7_060_carPaint_1']
sources=[bpy.data.objects[n] for n in names]
trees=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]) for o in sources]
WIDTH=.0015;OFFSET=.0011
mat=bpy.data.materials.new('M_QuadLines_OfflinePreview');mat.diffuse_color=(.5,.85,.8,1)
paths={};centres=[];missing={}
def cast_top(x,y):
    p,n,idx,d=trees[0].ray_cast(Vector((x,y,2)),Vector((0,0,-1)))
    if p is None or n.z<.3:return None
    return p,n
def bonnet(u,v):
    y=.88*u;s=abs(u)
    rear=1.145-.21*s*s-.12*s**8
    front=2.310-.030*s*s-.325*s**6
    return cast_top(rear+(front-rear)*v,y)
def side_hit(theta,r,side):
    x=1.5104+r*math.cos(theta);z=.3824+r*math.sin(theta)
    if not(.855<x<2.15 and .435<z<1.10):return None
    hits=[]
    for tree in trees:
        p,n,idx,d=tree.ray_cast(Vector((x,side*2,z)),Vector((0,-side,0)))
        if p is not None and side*n.y>.24 and side*p.y>.888:hits.append((p,n))
    return max(hits,key=lambda a:side*a[0].y) if hits else None
def add_samples(group,samples):
    current=[]
    def flush():
        if len(current)>3:paths.setdefault(group,[]).append(list(current))
        current.clear()
    for hit in samples:
        if hit is None:
            flush();missing[group]=missing.get(group,0)+1;continue
        p,n=hit
        if current and (p-current[-1][0]).length>.015:flush()
        current.append((p,n))
    flush()
for i in range(15):add_samples('Hood',[bonnet(-1+2*i/14,j/300) for j in range(301)])
for j in range(10):add_samples('Hood',[bonnet(-1+2*i/440,j/9) for i in range(441)])
for side,label in [(1,'Fender_L'),(-1,'Fender_R')]:
    # Smooth authored arch limits, inside the measured valid painted ranges.
    # Avoid following vent notches: these caused sharp turns in v02's contour.
    def field(u,v):
        deg=25+140*u;theta=math.radians(deg)
        lo=.523+.031*math.cos(theta)**2
        hi=.605+.060*math.exp(-((deg-120)/40)**2)
        return side_hit(theta,lo+v*(hi-lo),side)
    for j in range(3):add_samples(label,[field(i/648,j/2) for i in range(649)])
    for i in range(13):add_samples(label,[field(i/12,j/160) for j in range(161)])
objects=[];report={'version':VERSION,'source_blend':original_path,'width_m':WIDTH,'offset_m':OFFSET,'groups':{},'description':'Authored display quad-flow lines; original source is triangulated.'}
for group,segments in paths.items():
    verts=[];faces=[]
    for pts in segments:
        base=len(verts)
        for k,(p,n) in enumerate(pts):
            n=n.normalized();t=(pts[min(k+1,len(pts)-1)][0]-pts[max(k-1,0)][0]).normalized()
            w=t.cross(n).normalized()
            # Six-sided fine tube gives reliable silhouette and both view directions.
            for q in range(6):
                angle=q*math.tau/6
                verts.append(tuple(p+n*OFFSET+(n*math.cos(angle)+w*math.sin(angle))*WIDTH*.5))
            centres.append((p+n*OFFSET,group))
        for k in range(len(pts)-1):
            for q in range(6):
                a=base+k*6+q;b=base+k*6+(q+1)%6
                faces.append((a,b,b+6,a+6))
        faces.append(tuple(base+q for q in reversed(range(6))))
        last=base+(len(pts)-1)*6;faces.append(tuple(last+q for q in range(6)))
    mesh=bpy.data.meshes.new('QuadLineMesh_'+group+'_'+VERSION);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('SM_QuadLines_'+group+'_'+VERSION,mesh);col.objects.link(obj)
    obj.data.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    # Purpose-made UVs for valid tangents; no changes to source vehicle UVs.
    uv=mesh.uv_layers.new(name='UVMap')
    for p in mesh.polygons:
        for k,li in enumerate(p.loop_indices):
            if len(p.loop_indices)==4:uv.data[li].uv=[(0,0),(1,0),(1,1),(0,1)][k]
            else:uv.data[li].uv=(.5+.45*math.cos(k*math.tau/len(p.loop_indices)),.5+.45*math.sin(k*math.tau/len(p.loop_indices)))
    obj['purpose']='Surface quad display overlay; not recovered source topology';objects.append(obj)
    report['groups'][group]={'segments':len(segments),'vertices':len(verts),'faces':len(faces),'samples':sum(len(s) for s in segments)}
distances=[]
for p,group in centres:
    candidates=[b.find_nearest(p) for b in (trees[:1] if group=='Hood' else trees)]
    distances.append(min(h[3] for h in candidates if h[0] is not None))
report['surface_distance_m']={'min':min(distances),'max':max(distances),'mean':sum(distances)/len(distances)}
report['skipped_samples_at_boundaries']=missing
for o in bpy.context.selected_objects:o.select_set(False)
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
settings=dict(filepath=str(dest),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_space_transform=True,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,use_triangles=True,use_custom_props=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',embed_textures=False)
bpy.ops.export_scene.fbx(**settings)
# Copy save preserves the original file and keeps it as the open source context.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('YU7_QuadStudy_'+VERSION+'.blend')),copy=True,check_existing=False)
(OUT/'reports'/('geometry_'+VERSION+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
with (ROOT/'DEV_HISTORY.md').open('a',encoding='utf-8') as f:
    f.write('\n- 线框 '+VERSION+' 改进：MRQ v02 两视图成功，亮度 100 在棚内 EV9/bias+1 下呈浅青白，未改变车漆。近景发现自动外边界受通风口影响出现折线；改用测量有效范围内的平滑解析轮拱边界，减少为三条弧线/两排 quad，13 条径向线共用端点，避开通风口凹槽。输出新版本，不覆盖 v01/v02，待 UE 渲染确认。\n')
print(json.dumps(report,indent=2))
