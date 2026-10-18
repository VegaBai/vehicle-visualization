"""Author a shared, closed cube-sphere quad display field on exterior paint.

All six cage faces share boundary coordinates. Ray hits are clipped to the
outermost source-vehicle surface, preventing lines on wheels/glass/interior.
This adds renderable curves, not original topology. Editor preparation only.
"""
import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_QUAD_BODY'
VERSION=globals().get('VERSION','v01')
dest=OUT/('YU7_BodyLines_'+VERSION+'.fbx')
assert not dest.exists(),'Use a new version'
assert 'YU7_QuadStudy_' in bpy.data.filepath or 'YU7_BodyStudy_' in bpy.data.filepath
start=time.time();verts=[];faces=[];owners=[];allowed=[]
originals=sorted([o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SM_YU7_')],key=lambda o:o.name)
assert len(originals)==121
for o in originals:
    base=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    for f in o.data.polygons:
        faces.append([base+i for i in f.vertices]);owners.append(o.name)
        mat=o.data.materials[f.material_index] if len(o.data.materials)>f.material_index else None
        # The outermost hit must be a painted exterior panel. Inner-facing
        # polygons are rejected below by view-facing normal and height.
        allowed.append(bool(mat and 'CarPaint' in mat.name))
tree=BVHTree.FromPolygons(verts,faces)
center=Vector((0,0,.72));axes=(2.65,1.06,.86)
counts=(30,14,10);WIDTH=.0015;OFFSET=.0011
col=bpy.data.collections.new('YU7_BODY_QUAD_'+VERSION);bpy.context.scene.collection.children.link(col)
paths={};missing=0;hits_by_object={};seam_keys=set();seen_lines=set()

def cast_cube(q,centre=center,scales=axes,target_names=None):
    # Spherified cube has no polar fan: every cage face contains only quads.
    s=[]
    for i in range(3):
        a=q[(i+1)%3]**2;b=q[(i+2)%3]**2
        s.append(q[i]*math.sqrt(max(0,1-a/2-b/2+a*b/3)))
    direction=Vector([s[i]*scales[i] for i in range(3)]).normalized()
    p,n,index,d=tree.ray_cast(centre+direction*8,-direction,8)
    if p is None or n.dot(direction)<.08 or p.z<.30:return None
    if target_names is not None:
        if owners[index] not in target_names:return None
    elif not allowed[index]:return None
    return p,n,owners[index]

def add_path(label,samples):
    current=[]
    def flush():
        if len(current)>=3:
            length=sum((current[i][0]-current[i-1][0]).length for i in range(1,len(current)))
            if length>.018:paths.setdefault(label,[]).append(list(current))
        current.clear()
    for hit in samples:
        if hit is None:flush();continue
        p,n,name=hit
        # Stop at panel gaps or abrupt occlusion transitions, never bridge holes.
        if current and ((p-current[-1][0]).length>.018 or name!=current[-1][2]):flush()
        current.append((p,n,name));hits_by_object[name]=hits_by_object.get(name,0)+1
    flush()

def cube_grid(label,subdivisions,centre=center,scales=axes,target_names=None):
    keys=set()
    for fixed_axis in range(3):
        other=[i for i in range(3) if i!=fixed_axis]
        for sign in [-1,1]:
            for constant_axis,variable_axis in [other,other[::-1]]:
                for j in range(subdivisions[constant_axis]+1):
                    constant=-1+2*j/subdivisions[constant_axis]
                    a=[0.,0.,0.];b=[0.,0.,0.]
                    a[fixed_axis]=b[fixed_axis]=sign
                    a[constant_axis]=b[constant_axis]=constant
                    a[variable_axis]=-1;b[variable_axis]=1
                    key=tuple(sorted([tuple(round(v,6) for v in a),tuple(round(v,6) for v in b)]))
                    if key in keys:continue
                    keys.add(key)
                    # Sub-sampling resolution controls geometric smoothness only.
                    steps=1600 if variable_axis==0 else 900
                    if target_names:steps=160
                    samples=[]
                    for k in range(steps+1):
                        q=list(a);q[variable_axis]=-1+2*k/steps
                        samples.append(cast_cube(q,centre,scales,target_names))
                    add_path(label,samples)

cube_grid('Body',counts)
# Mirror housings use their own small connected cages; they are separate parts.
for side,label,names in [(1,'Mirror_L',{'SM_YU7_015_carMirror_bottom_2','SM_YU7_059_carMirror_top_2'}),(-1,'Mirror_R',{'SM_YU7_071_carMirror_bottom_2_1_','SM_YU7_066_carMirror_top_2_1_'})]:
    cube_grid(label,(4,4,3),Vector((.44,side*.965,1.167)),(.125,.12,.085),names)

def simplify_path(points,tolerance=.00010):
    # Ramer-Douglas-Peucker on actual offset centres. Bound line-surface
    # deviation to 0.1 mm, and keep an intermediate point at normal changes.
    coords=[p+n*OFFSET for p,n,name in points];keep={0,len(points)-1};stack=[(0,len(points)-1)]
    while stack:
        a,b=stack.pop()
        if b-a<2:continue
        delta=coords[b]-coords[a];length2=delta.length_squared
        worst=-1;split=None
        for k in range(a+1,b):
            t=max(0,min(1,(coords[k]-coords[a]).dot(delta)/length2)) if length2 else 0
            error=(coords[k]-coords[a]-delta*t).length
            # Tube silhouette must remain smooth at mesh hard-normal changes.
            normal=points[a][1].lerp(points[b][1],t).normalized()
            error=max(error,(points[k][1]-normal).length*WIDTH*.5)
            if error>worst:worst=error;split=k
        if worst>tolerance:keep.add(split);stack.extend([(a,split),(split,b)])
    return [points[i] for i in sorted(keep)]

raw_samples=sum(len(p) for segments in paths.values() for p in segments)
if VERSION!='v01':paths={key:[simplify_path(p) for p in segments] for key,segments in paths.items()}
gap_spans_removed=0
if VERSION not in {'v01','v02'}:
    # A single source object can include both sides of an open seam. Do not
    # connect even short spans whose interior floats above an actual gap.
    clipped={}
    for group,segments in paths.items():
        kept=[]
        for pts in segments:
            chunk=[pts[0]]
            for previous,current in zip(pts,pts[1:]):
                a=previous[0]+previous[1]*OFFSET;b=current[0]+current[1]*OFFSET
                if max(tree.find_nearest(a.lerp(b,t))[3] for t in [.25,.5,.75])>.0016:
                    if len(chunk)>1:kept.append(chunk)
                    chunk=[];gap_spans_removed+=1
                chunk.append(current)
            if len(chunk)>1:kept.append(chunk)
        clipped[group]=kept
    paths=clipped
objects=[];report={'version':VERSION,'description':'Closed shared cube-sphere quad field projected onto exterior paint; display lines, not recovered topology','original_objects':len(originals),'width_m':WIDTH,'offset_m':OFFSET,'cage_subdivisions':counts,'groups':{},'source_hit_counts':hits_by_object,'raw_samples':raw_samples,'simplification_error_m':0 if VERSION=='v01' else .00010,'gap_spans_removed':gap_spans_removed}
mat=bpy.data.materials.new('M_BodyLines_Offline_'+VERSION);mat.diffuse_color=(.52,.85,.79,1)
for group,segments in paths.items():
    vv=[];ff=[]
    for pts in segments:
        base=len(vv)
        for k,(p,n,name) in enumerate(pts):
            n=n.normalized();t=(pts[min(k+1,len(pts)-1)][0]-pts[max(k-1,0)][0]).normalized();w=t.cross(n).normalized()
            for q in range(6):
                angle=q*math.tau/6
                vv.append(tuple(p+n*OFFSET+(n*math.cos(angle)+w*math.sin(angle))*WIDTH*.5))
        for k in range(len(pts)-1):
            for q in range(6):
                a=base+k*6+q;b=base+k*6+(q+1)%6;ff.append((a,b,b+6,a+6))
        ff.append(tuple(base+q for q in reversed(range(6))))
        last=base+(len(pts)-1)*6;ff.append(tuple(last+q for q in range(6)))
    mesh=bpy.data.meshes.new('BodyLineMesh_'+group+'_'+VERSION);mesh.from_pydata(vv,[],ff);mesh.update()
    obj=bpy.data.objects.new('SM_BodyLines_'+group+'_'+VERSION,mesh);col.objects.link(obj);mesh.materials.append(mat)
    uv=mesh.uv_layers.new(name='UVMap')
    for p in mesh.polygons:
        p.use_smooth=True
        for k,li in enumerate(p.loop_indices):
            uv.data[li].uv=([(0,0),(1,0),(1,1),(0,1)][k] if len(p.loop_indices)==4 else (.5+.45*math.cos(k*math.tau/len(p.loop_indices)),.5+.45*math.sin(k*math.tau/len(p.loop_indices))))
    obj['purpose']='Authored full body quad display layer, not source topology'
    objects.append(obj);report['groups'][group]={'segments':len(segments),'vertices':len(vv),'faces':len(ff),'samples':sum(len(p) for p in segments)}
for collection in bpy.data.collections:
    if collection.name.startswith(('YU7_QUAD_STUDY_','YU7_BODY_QUAD_')) and collection!=col:collection.hide_viewport=True;collection.hide_render=True
for o in bpy.context.selected_objects:o.select_set(False)
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(dest),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_space_transform=True,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,use_triangles=True,use_custom_props=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('YU7_BodyStudy_'+VERSION+'.blend')),check_existing=False)
report['seconds']=time.time()-start
(OUT/'reports'/('geometry_'+VERSION+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
