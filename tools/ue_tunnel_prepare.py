import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');OUT=R/'art/YU7_TUNNEL_FLOW/reports'
E=unreal.EditorAssetLibrary;world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/QuadBodyStudy/Maps/Studio_YU7_QuadBody.Studio_YU7_QuadBody'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
dest='/Game/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow';assert not E.does_asset_exist(dest)
assert unreal.EditorLoadingAndSavingUtils.save_map(world,dest)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(dest)
RESULT={'map':dest,'protected_count':len(json.loads((OUT/'protected_before.json').read_text())),'native_math_api':{n:str(getattr(unreal,n,None).__doc__) for n in ['MaterialExpressionSmoothStep','MaterialExpressionPower','MaterialExpressionExponential2','MaterialExpressionTextureCoordinate','MaterialExpressionWorldPosition','MaterialExpressionVectorNoise','MaterialExpressionNoise','MaterialParameterCollectionFactoryNew','MaterialExpressionSaturate','MovieSceneSequencePlaybackSettings']}}
(OUT/'prepared.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
