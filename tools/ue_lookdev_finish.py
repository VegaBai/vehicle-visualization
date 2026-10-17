"""Finish the saved lookdev session and remove its temporary editor callback."""
import unreal,json,inspect,hashlib
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/lookdev'
E=unreal.EditorAssetLibrary
audit=json.loads((OUT/'final_audit.json').read_text(encoding='utf-8'))
assert audit['variant_combinations_verified']==24
assert audit['original_imported_assets_unchanged']
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
for group,name,file in [('Paint','Mineral Teal','beauty_mineral_teal.png'),('Paint','Pearl White','beauty_pearl_white.png'),('Paint','Graphite','beauty_graphite_contrast.png')]:
    path=OUT/file;assert path.exists()
    lvs.get_variant_set_by_name(group).get_variant_by_name(name).set_thumbnail_from_file(str(path))
E.save_loaded_asset(lvs)
E.sync_browser_to_objects([lvs.get_path_name()])
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([lvs])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 4')
RESULT={'saved':True,'thumbnails':3,'active_map':world.get_path_name(),'runner_stopped':False}
for info in inspect.stack():
    if Path(info.filename).name=='ue_editor_jobs.py' and info.function=='tick':
        unreal.unregister_slate_post_tick_callback(info.frame.f_globals['HANDLE']);RESULT['runner_stopped']=True;break
assert RESULT['runner_stopped']
(ROOT/'art/YU7_UNREAL/reports/ue_jobs/request.json').write_text(json.dumps({'id':'lookdev_session_closed','stop':True}),encoding='utf-8')
manifest={str(p.relative_to(ROOT/'VehicleStudio')):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (ROOT/'VehicleStudio/Content/YU7').rglob('*') if p.is_file()}
(OUT/'output_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'session_final.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
