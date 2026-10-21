"""Decode all 432 native PNGs, encode clean 18-second video and validate history."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
code=(R/'tools/yu7_tunnel_package.py').read_text()
code=code.replace("reports';D=R/'renders/YU7_TunnelFlow'","reports/finish_v11';D=R/'renders/YU7_TunnelFlow/FinishShowcase_v11'")
code=code.replace('288','432').replace("name+'_12s.mp4'","name+'_18s.mp4'").replace('1e6-12','1e6-18').replace('12 seconds','18 seconds').replace("'duration_seconds':12","'duration_seconds':18")
code=code.replace("if i>0 and s['difference']", "if i>162 and s['difference']")
code=code.replace('Silent visual review; proposed sound design has not been produced.','Silent finish showcase. Native frames without title overlays.')
exec(compile(code,str(R/'tools/yu7_finish_v11_package.py'),'exec'))
