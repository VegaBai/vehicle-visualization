"""Versioned v11 MRQ using the previously validated native render settings."""
from pathlib import Path
R=Path('C:/github2/vehicle_visualization')
code=(R/'tools/ue_ad_v09_render.py').read_text()
code=code.replace('reports/art_direction_v09','reports/finish_v11').replace('/ArtDirection_v09','/FinishShowcase_v11').replace('Studio_YU7_TunnelFlow_AD_v09','Studio_YU7_FinishShowcase_v11').replace('LS_YU7_TunnelFlow_AD_v09_12s','LS_YU7_FinishShowcase_v11_18s').replace("('Motion',0,288)","('Motion',0,432)")
exec(compile(code,str(R/'tools/ue_finish_v11_render.py'),'exec'))
