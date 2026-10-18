"""One-time map copy, keeping all original packages untouched."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero.Studio_YU7_MineralHero'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
MAP='/Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy'
assert not E.does_asset_exist(MAP),'Do not overwrite the study'
assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)
# Clear Variant Manager caches before any map reload, even though hero is unbound.
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(MAP)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
RESULT={'map':world.get_path_name(),'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]}
(OUT/'map_prepared.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
with (ROOT/'DEV_HISTORY.md').open('a',encoding='utf-8') as f:f.write('\n- UE 编辑器确认当前为已保存的 MineralHero 地图、无脏内容。另存 /Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy 并先清 LVS 缓存再加载副本成功；尚未导入线框。原镜头、Lookdev 及导入模型不编辑。\n')
