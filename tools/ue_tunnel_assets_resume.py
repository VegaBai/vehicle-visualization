"""Resume after the 5 meshes and empty MPC were created; do not reimport."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
meshes=[unreal.load_asset(p) for p in E.list_assets(D+'/Meshes')];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)];assert len(meshes)==5
mpc=unreal.load_asset(D+'/Materials/MPC_TunnelFlow');assert mpc and len(mpc.get_editor_property('scalar_parameters'))==0
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('p=unreal.CollectionScalarParameter()'):]
exec(compile(code,'ue_tunnel_assets_resume_body','exec'))
