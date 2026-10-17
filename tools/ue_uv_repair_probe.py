import json
from pathlib import Path
import unreal
docs={n:str(getattr(unreal,n).__doc__) for n in ['GeometryScriptCopyMeshToAssetOptions','GeometryScriptMeshWriteLOD']}
names=['YU7_Unreal_SM_YU7_042_carInternal_SteeringWheel_Bottom','YU7_Unreal_SM_YU7_071_carMirror_bottom_2_1_']
rows=[]
for name in names:
    mesh=unreal.load_asset('/Game/Vehicles/YU7_Prepared/Meshes/'+name)
    dm,result=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,unreal.DynamicMesh(),unreal.GeometryScriptCopyMeshFromAssetOptions(apply_build_settings=False,request_tangents=True),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL,lod_index=0))
    bad=[];minimum=1
    for t in range(dm.get_triangle_count()):
        a,b,c,valid=unreal.GeometryScript_MeshQueries.get_triangle_u_vs(dm,0,t)
        area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))
        minimum=min(minimum,area)
        if area<1e-11:bad.append({'triangle':t,'area2':area,'uv':[[v.x,v.y] for v in [a,b,c]]})
    rows.append({'name':name,'triangles':dm.get_triangle_count(),'bad':bad,'min_area':minimum})
    dm,result=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,unreal.DynamicMesh(),unreal.GeometryScriptCopyMeshFromAssetOptions(apply_build_settings=False,request_tangents=True),unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.RENDER_DATA,lod_index=0))
    bad=[]
    for t in range(dm.get_triangle_count()):
        a,b,c,valid=unreal.GeometryScript_MeshQueries.get_triangle_u_vs(dm,0,t)
        area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))
        if area==0:bad.append({'triangle':t,'area2':area,'uv':[[v.x,v.y] for v in [a,b,c]]})
    rows[-1]['render_bad']=bad
RESULT={'options':docs,'source_uvs':rows}
