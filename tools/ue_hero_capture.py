import unreal,json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/hero')
r=json.loads((OUT/'capture_request.json').read_text(encoding='utf-8-sig'))
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 64')
unreal.AutomationLibrary.take_high_res_screenshot(r.get('width',1920),r.get('height',1080),str(OUT/Path(r['filename']).name),delay=3.)
RESULT={'requested':r['filename']}
