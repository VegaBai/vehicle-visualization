"""Reuse the validated MRQ configuration in the isolated v10 asset/output roots."""
from pathlib import Path
R=Path('C:/github2/vehicle_visualization')
code=(R/'tools/ue_ad_v09_render.py').read_text()
code=code.replace('reports/art_direction_v09','reports/roof_smooth_v10').replace('/ArtDirection_v09','/RoofSmooth_v10').replace('TunnelFlow_AD_v09','TunnelFlow_Smooth_v10')
exec(compile(code,str(R/'tools/ue_smooth_v10_render.py'),'exec'))
