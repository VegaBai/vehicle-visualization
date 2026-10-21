"""Broad smooth roof profiles: no pointwise clamping to body edges."""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('C:/github2/vehicle_visualization')
O=R/'art/YU7_TUNNEL_FLOW/reports/roof_smooth_v10';P=R/'art/YU7_TUNNEL_FLOW/prepared'
assert (O/'protected_before.json').exists()
assert Path(bpy.data.filepath).name=='YU7_RoofAirflow_AD_v09.blend' and not bpy.data.is_dirty
assert not (P/'YU7_RoofAirflow_Smooth_v10.fbx').exists()
originals=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('SM_YU7_')]
assert len(originals)==121
data=json.loads((R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09/roof_centerlines.json').read_text())
col=bpy.data.collections.new('YU7_ROOF_SMOOTH_v10');bpy.context.scene.collection.children.link(col)
objects=[];points=[];metrics=[]
sigma=.35;half=140
u=np.arange(-half,half+1)*.01;kernel=np.exp(-.5*(u/sigma)**2);kernel/=kernel.sum()
for row,source in zip(data['lanes'],data['points']):
    j=row['lane'];a=np.array(source);z=a[:,2].copy()
    # Linear extension preserves endpoint tangents. One broad convolution removes
    # local radar/roof-envelope corners; a uniform 2.5 cm lift retains clearance.
    padded=np.concatenate([z[0]+np.arange(-half,0)*(z[1]-z[0]),z,z[-1]+np.arange(1,half+1)*(z[-1]-z[-2])])
    a[:,2]=np.convolve(padded,kernel,mode='valid')+.025
    lane=[Vector(p) for p in a];radius=row['radius_m'];verts=[];faces=[];uvs=[]
    for k,p in enumerate(lane):
        tangent=(lane[min(k+1,1100)]-lane[max(k-1,0)]).normalized()
        normal=Vector((0,0,1));normal=(normal-tangent*normal.dot(tangent)).normalized();side=tangent.cross(normal)
        for n in range(6):
            verts.append(tuple(p+radius*(normal*math.cos(n*math.tau/6)+side*math.sin(n*math.tau/6))))
            uvs.append((k/1100,j/6))
    for k in range(1100):
        for n in range(6):
            v=k*6+n;w=k*6+(n+1)%6;faces.append((v,w,w+6,v+6))
    mesh=bpy.data.meshes.new('SM_RoofSmooth_v10_Lane'+str(j));mesh.from_pydata(verts,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='FlowCoordinate')
    for poly in mesh.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
    obj=bpy.data.objects.new(mesh.name,mesh);col.objects.link(obj);objects.append(obj);points.append(a.tolist())
    metrics.append({'lane':j,'before_max_abs_z_second_derivative_per_m':float(np.max(np.abs(np.diff(z,2)))/.0001),'after_max_abs_z_second_derivative_per_m':float(np.max(np.abs(np.diff(a[:,2],2)))/.0001),'min_height_change_m':float(np.min(a[:,2]-z)),'max_height_change_m':float(np.max(a[:,2]-z))})
for obj in bpy.context.selected_objects:obj.select_set(False)
for obj in objects:obj.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(P/'YU7_RoofAirflow_Smooth_v10.fbx'),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_space_transform=True,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,use_triangles=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'YU7_RoofAirflow_Smooth_v10.blend'),check_existing=False)
(O/'roof_centerlines.json').write_text(json.dumps({'lanes':data['lanes'],'points':points}),encoding='utf-8')
result={'method':'Gaussian profile smoothing with linear endpoint extension, no local surface clamp','sigma_m':sigma,'uniform_lift_m':.025,'lanes':data['lanes'],'curvature_metrics':metrics,'triangles':92400,'original_objects_preserved':121,'WPO_unchanged':True,'illustrative_not_CFD':True,'status':'Authored; distance and native render pending'}
(O/'roof_geometry.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
