"""Audit v10 persistence, original geometry, unchanged shared shading and bindings."""
from pathlib import Path
R=Path('C:/github2/vehicle_visualization')
code=(R/'tools/ue_ad_v09_audit.py').read_text()
code=code.replace('reports/art_direction_v09','reports/roof_smooth_v10').replace("D='/Game/YU7/TunnelFlow/ArtDirection_v09'","D='/Game/YU7/TunnelFlow/RoofSmooth_v10'").replace('TunnelFlow_AD_v09','TunnelFlow_Smooth_v10')
code=code.replace("m.get_path_name().startswith(D+'/Materials/')","m.get_path_name().startswith('/Game/YU7/TunnelFlow/ArtDirection_v09/Materials/')")
code=code.replace("if label.endswith('RoofAirflow'):\n","if label.endswith('RoofAirflow'):\n            assert c.static_mesh.get_path_name().startswith(D+'/Meshes/')\n")
exec(compile(code,str(R/'tools/ue_smooth_v10_audit.py'),'exec'))
