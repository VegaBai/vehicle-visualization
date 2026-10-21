"""Author versioned seven-lane geometry; read the original vehicle for clearance."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';P=R/'art/YU7_TUNNEL_FLOW/prepared'
assert not (P/'YU7_RoofAirflow_AD_v09.fbx').exists()
assert Path(bpy.data.filepath).name=='YU7_RoofAirflow_v01.blend'
assert not bpy.data.is_dirty
originals=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SM_YU7_')];assert len(originals)==121
vs=[];fs=[]
for o in originals:
    b=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([[b+i for i in p.vertices] for p in o.data.polygons])
tree=BVHTree.FromPolygons(vs,fs)
old=bpy.data.objects['SM_RoofAirflow_v01']
def smooth(a,b,x):
    u=max(0.,min(1.,(x-a)/(b-a)));return u*u*(3-2*u)
def offset(p,l,t):
    env=smooth(.025,.12,p)*(1-smooth(.9,1,p))*smooth(1.5,2,t)
    tail=smooth(.55,.78,p)
    stable=.7 if l>=5/6-.001 else 1.
    z=((2.5+11*tail)*math.sin(math.tau*(1.5*p-.22*t+.55*l))+.65*math.sin(math.tau*(2.5*p-.18*t-.5*l)))*env*stable
    y=(3.0+8*tail)*math.sin(math.tau*(1.25*p-.20*t+.65*l))*env*stable
    return y,z
ys=[-.62,-.40,-.17,.06,.28,.47,.65]
col=bpy.data.collections.new('YU7_ROOF_AD_v09');bpy.context.scene.collection.children.link(col)
objects=[];records=[];points=[]
for j,y0 in enumerate(ys):
    lane=[]
    for k in range(1101):
        x=3.5-k*.01;p=k/1100
        ring=[old.data.vertices[j*1101*6+k*6+n].co for n in range(6)]
        old_center=sum(ring,Vector())/6
        # Remove the old equal-height arches locally, keeping a smooth silhouette.
        near=smooth(-3.,-2.3,x)*(1-smooth(1.5,2.5,x))
        reduction=[.11,.075,.025,-.015,.03,.08,.12][j]
        z=old_center.z-reduction*near
        y=y0*(1+.17*(1-math.exp(-max(0.,-x-2.3)*.6)))
        # Clearance envelope includes nearby lateral WPO, radar, antenna and spoiler.
        tops=[]
        for dy in [-.06,-.03,0,.03,.06]:
            hit=tree.ray_cast(Vector((x,y+dy,4)),Vector((0,0,-1)),5)[0]
            if hit is not None and -2.6<x<2.6:tops.append(hit.z)
        if tops:z=max(z,max(tops)+.18+(.015 if j%2 else .035))
        lane.append(Vector((x,y,z)))
    # Smooth discrete safety-envelope corners without reducing their height.
    for _ in range(5):
        zz=[v.z for v in lane]
        for k in range(3,len(lane)-3):lane[k].z=max(zz[k],sum(zz[k-3:k+4])/7)
    verts=[];faces=[];uvs=[];radius=.0026 if j>=5 else .0015
    for k,p in enumerate(lane):
        tangent=(lane[min(k+1,1100)]-lane[max(k-1,0)]).normalized()
        normal=Vector((0,0,1));normal=(normal-tangent*normal.dot(tangent)).normalized();side=tangent.cross(normal)
        for n in range(6):
            verts.append(tuple(p+radius*(normal*math.cos(n*math.tau/6)+side*math.sin(n*math.tau/6))));uvs.append((k/1100,j/6))
    for k in range(1100):
        for n in range(6):a=k*6+n;b=k*6+(n+1)%6;faces.append((a,b,b+6,a+6))
    mesh=bpy.data.meshes.new('SM_RoofAD_v09_Lane'+str(j));mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='FlowCoordinate')
    for poly in mesh.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
    obj=bpy.data.objects.new(mesh.name,mesh);col.objects.link(obj);objects.append(obj)
    points.append([list(p) for p in lane]);records.append({'lane':j,'y_center_m':y0,'radius_m':radius,'role':'primary' if j>=5 else 'secondary'})
for o in bpy.context.selected_objects:o.select_set(False)
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(P/'YU7_RoofAirflow_AD_v09.fbx'),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_space_transform=True,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,use_triangles=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'YU7_RoofAirflow_AD_v09.blend'),check_existing=False)
(O/'roof_centerlines.json').write_text(json.dumps({'lanes':records,'points':points}),encoding='utf-8')
report={'lanes':records,'vertices':len(objects)*6606,'triangles':92400,'original_objects_preserved':len(originals),'status':'Geometry authored; clearance and rendered motion pending','body_u':'(2.5-x)/5 = 2.2*roof_U-0.2; roof UV.x=(3.5-x)/11','illustrative_not_CFD':True}
(O/'roof_geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
