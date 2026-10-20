import unreal,json,hashlib
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow';E=unreal.EditorAssetLibrary
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_path_name()==D+'/Maps/Studio_YU7_TunnelFlow.Studio_YU7_TunnelFlow'
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages();assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
b=D+'/Maps/Studio_YU7_TunnelFlow_BeforePulse_v07';assert not E.does_asset_exist(b);assert E.duplicate_asset(D+'/Maps/Studio_YU7_TunnelFlow',b);assert E.save_asset(b)
files=[p for p in (R/'VehicleStudio/Content/YU7/TunnelFlow').rglob('*') if p.is_file() and p.name!='Studio_YU7_TunnelFlow.umap']
files.extend(p for p in (R/'renders/YU7_TunnelFlow').iterdir() if p.is_file())
snap=[{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
(O/'pulse_protected_before.json').write_text(json.dumps(snap,indent=2),encoding='utf-8')
RESULT={'backup':b,'protected_files':len(snap),'transform_source_enum':[x for x in dir(unreal.MaterialVectorCoordTransformSource) if x.startswith('TRANSFORM')],'transform_target_enum':[x for x in dir(unreal.MaterialVectorCoordTransform) if x.startswith('TRANSFORM')]}
