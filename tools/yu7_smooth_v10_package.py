"""Validate native frames and encode the corrected shot."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1]
code=(R/'tools/yu7_tunnel_package.py').read_text()
code=code.replace("O=R/'art/YU7_TUNNEL_FLOW/reports';D=R/'renders/YU7_TunnelFlow'","O=R/'art/YU7_TUNNEL_FLOW/reports/roof_smooth_v10';D=R/'renders/YU7_TunnelFlow/RoofSmooth_v10'")
exec(compile(code,str(R/'tools/yu7_smooth_v10_package.py'),'exec'))
