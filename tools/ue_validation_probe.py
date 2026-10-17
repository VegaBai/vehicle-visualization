import json
from pathlib import Path
import unreal
classes = ['GeometryScript_List','GeometryScript_MeshQueries','DynamicMesh','GeometryScriptMeshReadLOD','GeometryScriptLODType','MeshBuildSettings','StaticMeshComponent','MaterialEditingLibrary','MaterialStatistics']
docs = {}
for name in classes:
    cls = getattr(unreal,name,None)
    docs[name] = {'doc': str(getattr(cls,'__doc__','unavailable')), 'methods':{x:str(getattr(cls,x).__doc__) for x in dir(cls) if not x.startswith('_') and any(t in x for t in ['list','triangle','normal','position','count','statistics','bound','material','uv','tangent'])}} if cls else None
Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/ue_validation_api.json').write_text(json.dumps(docs,indent=2),encoding='utf-8')
assets = [unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets('/Game/Vehicles/YU7_Prepared/Meshes')]
mesh = next(m for m in assets if isinstance(m,unreal.StaticMesh))
opts = unreal.GeometryScriptCopyMeshFromAssetOptions(apply_build_settings=True,request_tangents=True)
lod = unreal.GeometryScriptMeshReadLOD(lod_type=unreal.GeometryScriptLODType.RENDER_DATA,lod_index=0)
dm, result = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,unreal.DynamicMesh(),opts,lod)
RESULT = {'mesh':mesh.get_name(),'copy_result':str(result),'triangles':dm.get_triangle_count(),'normals':str(unreal.GeometryScript_MeshQueries.get_triangle_normals(dm,0)),'tangents':str(unreal.GeometryScript_MeshQueries.get_triangle_normal_tangents(dm,0)),'bounds':str(mesh.get_bounds()),'query_methods':dir(unreal.GeometryScript_MeshQueries)}
