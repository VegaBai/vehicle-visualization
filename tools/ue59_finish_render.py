from pathlib import Path
import unreal,json
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_UNREAL/reports/ue59_runtime_r01'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
assert json.loads((O/'finish_pie_audit.json').read_text())['status']=='passed'
r=dict(name='FinishFlow_UE59_r01',frames=[0,30,60,90,120,156,288,300,420],width=1280,height=720,temporal=8)
(O/'render_request.json').write_text(json.dumps(r))
code=(R/'tools/ue_ad_v09_render.py').read_text()
code=code.replace('art/YU7_TUNNEL_FLOW/reports/art_direction_v09','art/YU7_UNREAL/reports/ue59_runtime_r01').replace("D='/Game/YU7/TunnelFlow/ArtDirection_v09'","D='/Game/YU7/TunnelFlow/FinishShowcase_v11'").replace('Studio_YU7_TunnelFlow_AD_v09','Studio_YU7_FinishShowcase_v11').replace('LS_YU7_TunnelFlow_AD_v09_12s','LS_YU7_FinishShowcase_v11_18s').replace('renders/YU7_TunnelFlow/ArtDirection_v09','renders/UE59_Compatibility_r01')
exec(compile(code,'ue59_finish_render','exec'))
