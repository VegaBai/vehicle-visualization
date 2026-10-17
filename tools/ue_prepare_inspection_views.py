import json
from pathlib import Path
import unreal
ROOT=Path('C:/github2/vehicle_visualization')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Maps/Studio_YU7.Studio_YU7'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
current={a.get_actor_label():a for a in actors.get_all_level_actors()}
views=[('CAM_YU7_Front',(-750,650,300),(0,0,75)),('CAM_YU7_Rear',(750,-650,270),(0,0,75)),('CAM_YU7_Side',(0,1080,205),(0,0,75))]
for label,pos,look in views:
    loc=unreal.Vector(*pos);rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(*look))
    camera=current.get(label) or actors.spawn_actor_from_class(unreal.CineCameraActor,loc,rot)
    camera.set_actor_label(label);camera.set_folder_path('YU7/InspectionCameras')
    camera.set_actor_location_and_rotation(loc,rot,False,True)
    comp=camera.get_cine_camera_component()
    comp.set_editor_property('current_focal_length',50.0)
    comp.set_editor_property('current_aperture',8.0)
    comp.set_editor_property('filmback',unreal.CameraFilmbackSettings(sensor_width=36.0,sensor_height=20.25))
    comp.set_editor_property('focus_settings',unreal.CameraFocusSettings(focus_method=unreal.CameraFocusMethod.DISABLE))
    current[label]=camera
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
key=level.get_active_viewport_config_key()
front=current['CAM_YU7_Front']
level.set_level_viewport_camera_info(front.get_actor_location(),front.get_actor_rotation(),key)
level.set_level_viewport_fov(39.598,key)
level.editor_set_viewport_realtime(True,key)
actors.clear_actor_selection_set()
assert level.save_current_level()
unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 64')
task=unreal.AutomationLibrary.take_high_res_screenshot(1600,900,str(ROOT/'art/YU7_UNREAL/reports/ue_front.png'),delay=3.0)
RESULT={'cameras':[v[0] for v in views],'screenshot_requested':'ue_front.png'}
