"""Validate all native frames and encode v09 media without changing historical outputs."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1]
source=(R/'tools/yu7_tunnel_package.py').read_text()
source=source.replace("O=R/'art/YU7_TUNNEL_FLOW/reports';D=R/'renders/YU7_TunnelFlow'","O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D=R/'renders/YU7_TunnelFlow/ArtDirection_v09'")
exec(compile(source,'v09_media_validation','exec'))
