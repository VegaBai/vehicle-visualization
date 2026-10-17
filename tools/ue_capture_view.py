"""Capture a requested inspection view using UE, with no external renderer."""
import json
from pathlib import Path
import unreal
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports')
config=json.loads((OUT/'ue_capture_request.json').read_text(encoding='utf-8-sig'))
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()==config['camera'])
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
key=level.get_active_viewport_config_key()
level.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),key)
level.set_level_viewport_fov(39.598,key)
actors.clear_actor_selection_set()
if config.get('buffer'):
    unreal.AutomationLibrary.set_editor_viewport_visualize_buffer(config['buffer'])
else:
    unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
filename=OUT/Path(config['filename']).name
unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(filename),delay=3.0)
RESULT={'requested':str(filename),'camera':camera.get_actor_label(),'buffer':config.get('buffer','Lit')}
