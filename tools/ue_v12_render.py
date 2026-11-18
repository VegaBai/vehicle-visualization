"""Versioned native MRQ in the isolated UE5.9 film map."""
from pathlib import Path
import unreal,json
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
assert json.loads((O/'scene_audit.json').read_text())['status']=='passed'
code=(R/'tools/ue_ad_v09_render.py').read_text()
code=code.replace('art/YU7_TUNNEL_FLOW/reports/art_direction_v09','art/YU7_TUNNEL_FLOW/reports/itasha_v12').replace("D='/Game/YU7/TunnelFlow/ArtDirection_v09'","D='/Game/YU7/TunnelFlow/ItashaShowcase_v12'").replace('Studio_YU7_TunnelFlow_AD_v09','Studio_YU7_ItashaShowcase_v12').replace('LS_YU7_TunnelFlow_AD_v09_12s','LS_YU7_ItashaShowcase_v12_24s').replace('renders/YU7_TunnelFlow/ArtDirection_v09','renders/YU7_TunnelFlow/ItashaShowcase_v12/frames').replace("[('Motion',0,288)]","[('Motion',0,576)]")
exec(compile(code,'v12_native_mrq','exec'))
