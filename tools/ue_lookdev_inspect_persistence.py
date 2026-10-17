import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/lookdev'
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=A.get_all_level_actors()
hero=next(a for a in actors if a.get_actor_label()=='YU7_Hero')
parts=[a for a in actors if a.get_actor_label().startswith('YU7_VP_')]
rig=next(a for a in actors if a.get_actor_label()=='YU7_StudioLighting')
visible=[c for c in hero.get_components_by_class(unreal.StaticMeshComponent) if c.is_visible()]
assert len(parts)==21 and len(visible)==100
assert all(c.intensity==0. and not c.is_visible() for c in rig.get_components_by_class(unreal.RectLightComponent))
unreal.SystemLibrary.execute_console_command(hero,'r.HighResScreenshotDelay 64')
RESULT={'persisted_native_parts':len(parts),'persisted_visible_bp_parts':len(visible),'original_rig_disabled':True,'reload_api':unreal.EditorLoadingAndSavingUtils.reload_packages.__doc__}
(OUT/'persistence.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
