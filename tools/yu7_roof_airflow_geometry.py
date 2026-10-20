"""Editor preparation: seven smooth airflow ribbons over the entire roof silhouette."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/prepared'
assert not (O/'YU7_RoofAirflow_v01.fbx').exists()
assert Path(bpy.data.filepath).name=='YU7_TunnelEffects_v01.blend'
originals=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SM_YU7_')];assert len(originals)==121
vs=[];fs=[]
for o in originals:
    base=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([[base+i for i in p.vertices] for p in o.data.polygons])
tree=BVHTree.FromPolygons(vs,fs)
# Smooth cubic Hermite interpolation of measured roof-clearance control points.
anchors=[(-7.5,1.46),(-4.5,1.40),(-3.,1.39),(-2.4,1.46),(-1.75,1.65),(-1.1,1.77),(-.55,1.81),(0.,1.76),(.45,1.57),(1.1,1.30),(1.8,1.17),(2.5,1.02),(3.5,.99)]
def height(x):
    i=next(i for i in range(len(anchors)-1) if anchors[i][0]<=x<=anchors[i+1][0]);a,b=anchors[i],anchors[i+1];h=b[0]-a[0];t=(x-a[0])/h
    before=anchors[max(0,i-1)];after=anchors[min(len(anchors)-1,i+2)]
    m0=(b[1]-before[1])/(b[0]-before[0]);m1=(after[1]-a[1])/(after[0]-a[0])
    return (2*t**3-3*t*t+1)*a[1]+(t**3-2*t*t+t)*h*m0+(-2*t**3+3*t*t)*b[1]+(t**3-t*t)*h*m1
verts=[];faces=[];uvs=[];clearances=[];lanes=[]
for j in range(7):
    y0=(j-3)*.22;pts=[];lane_min=99
    for k in range(1101):
        x=3.5-k*.01;tail=max(0.,-x-2.4);spread=1+.22*(1-math.exp(-tail*.55))
        y=y0*spread;z=height(x)+.02+.16*(abs(y0)/.66)**1.5
        z+=.018*math.sin(tail*.8+j*.45)*(1-math.exp(-tail))
        p=Vector((x,y,z));hit=tree.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),5)[0]
        if hit is not None and -2.49<x<2.49:
            lane_min=min(lane_min,z-hit.z);assert z-hit.z>.065,(x,y,z,hit.z)
        pts.append(p)
    base=len(verts)
    for k,p in enumerate(pts):
        tangent=(pts[min(k+1,len(pts)-1)]-pts[max(0,k-1)]).normalized();normal=Vector((0,0,1));normal=(normal-tangent*normal.dot(tangent)).normalized();side=tangent.cross(normal)
        for n in range(6):
            q=p+(normal*math.cos(n*math.tau/6)+side*math.sin(n*math.tau/6))*.003
            verts.append(tuple(q));uvs.append(((3.5-p.x)/11.,j/6))
    for k in range(len(pts)-1):
        for n in range(6):a=base+k*6+n;b=base+k*6+(n+1)%6;faces.append((a,b,b+6,a+6))
    lanes.append({'lane':j,'y_center':y0,'min_clearance_m':lane_min});clearances.append(lane_min)
col=bpy.data.collections.new('YU7_ROOF_AIRFLOW_v01');bpy.context.scene.collection.children.link(col)
mesh=bpy.data.meshes.new('SM_RoofAirflow_v01');mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='FlowCoordinate')
for p in mesh.polygons:
    p.use_smooth=True
    for li in p.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
obj=bpy.data.objects.new('SM_RoofAirflow_v01',mesh);col.objects.link(obj)
for o in bpy.context.selected_objects:o.select_set(False)
obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(O/'YU7_RoofAirflow_v01.fbx'),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_space_transform=True,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,use_triangles=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'YU7_RoofAirflow_v01.blend'),check_existing=False)
report={'lanes':lanes,'min_clearance_m':min(clearances),'vertices':len(verts),'triangles':len(faces)*2,'original_objects_preserved':len(originals),'profile':'nose, windshield, roof, rear glass, high wake; authored illustrative airflow, not CFD','uv':'U progresses nose to wake; V lane, inverted on FBX import'}
(R/'art/YU7_TUNNEL_FLOW/reports/roof_geometry_v01.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
