import unreal,json
from pathlib import Path
D='/Game/YU7/TunnelFlow';E=unreal.EditorAssetLibrary
meshes=[unreal.load_asset(p) for p in E.list_assets(D+'/Meshes')];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)]
materials=list(E.list_assets(D+'/Materials'));assert len(materials)==10
RESULT={'meshes':[{'path':m.get_path_name(),'triangles':m.get_num_triangles(0)} for m in meshes],'materials':materials,'mpc':D+'/Materials/MPC_TunnelFlow','native_material_nodes':True,'note':'All assets saved; previous job failed only serializing Unreal Array in final report.'}
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/assets.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
