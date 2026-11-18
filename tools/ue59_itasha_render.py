from pathlib import Path
import unreal,json
R=Path('C:/github2/vehicle_visualization')
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
O=R/'art/YU7_UNREAL/reports/ue59_runtime_r01'
assert json.loads((O/'pie_audit.json').read_text())['status']=='passed'
(O/'render_request.json').write_text(json.dumps(dict(name='Itasha_UE59_r01',itasha='Rengoku',paint='Pearl White',views=['Beauty'],width=1920,height=1080)))
code=(R/'tools/ue_itasha_v01_render.py').read_text()
code=code.replace("O=R/'art/YU7_ITASHA/reports/v01'","O=R/'art/YU7_UNREAL/reports/ue59_runtime_r01'")
code=code.replace("R/'renders/YU7_Itasha_v01'","R/'renders/UE59_Compatibility_r01'")
exec(compile(code,'ue59_itasha_render','exec'))
