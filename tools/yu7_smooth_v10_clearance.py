"""Reuse the exact unchanged v09 WPO evaluator against v10 curves."""
from pathlib import Path
R=Path('C:/github2/vehicle_visualization')
code=(R/'tools/yu7_ad_v09_clearance.py').read_text()
code=code.replace("reports/art_direction_v09","reports/roof_smooth_v10")
exec(compile(code,str(R/'tools/yu7_smooth_v10_clearance.py'),'exec'))
