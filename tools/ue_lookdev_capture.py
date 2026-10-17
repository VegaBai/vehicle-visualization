import unreal,json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/lookdev')
r=json.loads((OUT/'capture_request.json').read_text(encoding='utf-8-sig'))
name=Path(r['filename']).name
unreal.AutomationLibrary.take_high_res_screenshot(r.get('width',1600),r.get('height',900),str(OUT/name),delay=3.)
RESULT={'requested':str(OUT/name)}
