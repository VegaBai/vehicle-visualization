import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
meshes=[unreal.load_asset(p) for p in E.list_assets(D+'/Meshes')];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)];assert len(meshes)==5
mpc=unreal.load_asset(D+'/Materials/MPC_TunnelFlow');assert mpc.get_scalar_parameter_names()==['ShotTime']
broken=unreal.load_asset(D+'/Materials/M_TunnelGrid');assert broken
M.delete_all_material_expressions(broken)
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('class Graph:'):]
code=code.replace("        assert not E.does_asset_exist(D+'/Materials/'+name)\n        self.m=T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());self.n=0", "        assert name=='M_TunnelGrid' or not E.does_asset_exist(D+'/Materials/'+name)\n        self.m=broken if name=='M_TunnelGrid' else T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());self.n=0")
exec(compile(code,'ue_tunnel_materials_resume_body','exec'))
