import unreal,json,math
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/lookdev')
request=json.loads((OUT/'view_request.json').read_text(encoding='utf-8-sig'))
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
manager=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_VariantManager')
for group,name in request.get('variants',{}).items(): assert manager.switch_on_variant_by_name(group,name)
camera=next(a for a in A.get_all_level_actors() if a.get_actor_label()==request.get('camera','CAM_YU7_Beauty'))
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key()
level.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),key)
c=camera.get_cine_camera_component()
level.set_level_viewport_fov(math.degrees(2*math.atan(c.filmback.sensor_width/(2*c.current_focal_length))),key)
A.clear_actor_selection_set()
unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
RESULT={'camera':camera.get_actor_label(),'variants':request.get('variants',{})}
