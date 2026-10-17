import collections
import json
import math
from pathlib import Path
import unreal
ROOT=Path('C:/github2/vehicle_visualization')
q=unreal.GeometryScript_MeshQueries
sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
report=[]
def read(mesh,kind):
    dm,result=unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,unreal.DynamicMesh(),unreal.GeometryScriptCopyMeshFromAssetOptions(apply_build_settings=False,request_tangents=True),unreal.GeometryScriptMeshReadLOD(lod_type=kind,lod_index=0))
    assert result==unreal.GeometryScriptOutcomePins.SUCCESS
    return dm
def key(dm,t):
    valid,*pts=q.get_triangle_positions(dm,t)
    return tuple(sorted(tuple(round(v,4) for v in (p.x,p.y,p.z)) for p in pts))
def geometry_normals(dm):
    values=collections.Counter()
    for t in range(dm.get_triangle_count()):
        valid,*pts=q.get_triangle_positions(dm,t)
        _,n0,n1,n2,ok=q.get_triangle_normals(dm,t)
        assert valid and ok
        for p,n in zip(pts,(n0,n1,n2)):
            values[tuple(round(v,5) for v in (p.x,p.y,p.z,n.x,n.y,n.z))]+=1
    return values
audit=json.loads((ROOT/'art/YU7_UNREAL/reports/ue_validation.json').read_text(encoding='utf-8'))
for old in audit['meshes']:
    if not old['zero_area_uv_triangles']:continue
    mesh=unreal.load_asset('/Game/Vehicles/YU7_Prepared/Meshes/'+old['name'])
    render=read(mesh,unreal.GeometryScriptLODType.RENDER_DATA)
    bad=set()
    for t in range(render.get_triangle_count()):
        a,b,c,valid=q.get_triangle_u_vs(render,0,t)
        if (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)==0:bad.add(key(render,t))
    source=read(mesh,unreal.GeometryScriptLODType.SOURCE_MODEL)
    before=geometry_normals(source)
    repairs=[]
    for t in range(source.get_triangle_count()):
        if key(source,t) not in bad:continue
        a,b,c,valid=q.get_triangle_u_vs(source,0,t)
        original=[[v.x,v.y] for v in (a,b,c)]
        points=[a,b,c]
        pairs=[(0,1,2),(1,2,0),(2,0,1)]
        i,j,k=max(pairs,key=lambda ids:(points[ids[1]].x-points[ids[0]].x)**2+(points[ids[1]].y-points[ids[0]].y)**2)
        u,v=points[i],points[j]
        dx=v.x-u.x;dy=v.y-u.y;length=math.hypot(dx,dy)
        if length<0.002:
            points=[unreal.Vector2D(a.x,a.y),unreal.Vector2D(a.x+0.002,a.y),unreal.Vector2D(a.x,a.y+0.002)]
        else:
            oldp=points[k]
            points[k]=unreal.Vector2D(oldp.x-dy/length*0.002,oldp.y+dx/length*0.002)
        _,ok=unreal.GeometryScript_UVs.set_mesh_triangle_u_vs(source,0,t,unreal.GeometryScriptUVTriangle(uv0=points[0],uv1=points[1],uv2=points[2]),True)
        assert ok
        repairs.append({'triangle':t,'old_uv':original,'new_uv':[[p.x,p.y] for p in points]})
    assert len(repairs)==len(bad),(len(repairs),len(bad))
    settings=sub.get_lod_build_settings(mesh,0)
    options=unreal.GeometryScriptCopyMeshToAssetOptions(enable_recompute_normals=False,enable_recompute_tangents=False,replace_materials=False,emit_transaction=True)
    _,result=unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(source,mesh,options,unreal.GeometryScriptMeshWriteLOD(lod_index=0))
    assert result==unreal.GeometryScriptOutcomePins.SUCCESS
    sub.set_lod_build_settings(mesh,0,settings)
    after=geometry_normals(read(mesh,unreal.GeometryScriptLODType.SOURCE_MODEL))
    assert before==after,'Geometry or authored normals changed unexpectedly'
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    report.append({'mesh':mesh.get_name(),'repaired_triangles':len(repairs),'geometry_and_authored_normals_preserved_rounded_1e_5':before==after,'repairs':repairs})
(ROOT/'art/YU7_UNREAL/reports/ue_uv_repairs.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
RESULT=report
