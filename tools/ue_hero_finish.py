"""Save the cinematic handoff and remove temporary editor job callbacks."""
import unreal,json,inspect,hashlib,math
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/hero'
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero.Studio_YU7_MineralHero'
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='CAM_YU7_MineralHero')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key()
level.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),key)
level.set_level_viewport_fov(math.degrees(2*math.atan(36/(2*camera.get_cine_camera_component().current_focal_length))),key)
level.editor_set_viewport_realtime(True,key)
actors.clear_actor_selection_set()
unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 4')
seq=unreal.load_asset('/Game/YU7/Cinematics/Sequences/LS_YU7_MineralHero_5s')
unreal.EditorAssetLibrary.sync_browser_to_objects([seq.get_path_name()])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
for name in ['_yu7_diag','_yu7_hero_render']:
    if hasattr(unreal,name):delattr(unreal,name)
manifest={p.relative_to(ROOT/'VehicleStudio').as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (ROOT/'VehicleStudio/Content/YU7/Cinematics').rglob('*') if p.is_file()}
(OUT/'output_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
RESULT={'saved':True,'active_map':world.get_path_name(),'native_sequence':seq.get_path_name(),'cinematic_files':len(manifest),'dirty_maps':[],'dirty_content':[],'runner_stopped':False}
for info in inspect.stack():
    if Path(info.filename).name=='ue_editor_jobs.py' and info.function=='tick':
        unreal.unregister_slate_post_tick_callback(info.frame.f_globals['HANDLE']);RESULT['runner_stopped']=True;break
assert RESULT['runner_stopped']
(ROOT/'art/YU7_UNREAL/reports/ue_jobs/request.json').write_text(json.dumps({'id':'hero_session_closed','stop':True}),encoding='utf-8')
(OUT/'session_final.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
