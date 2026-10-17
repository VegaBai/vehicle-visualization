import json
import runpy
from pathlib import Path
import unreal

ROOT = Path('C:/github2/vehicle_visualization')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
target = '/Game/YU7/Maps/Studio_YU7'
assert world.get_path_name() == '/Game/Studios/Levels/Studio_White.Studio_White', world.get_path_name()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'Unexpected unsaved map changes'
if not unreal.EditorAssetLibrary.does_asset_exist(target):
    assert unreal.EditorLoadingAndSavingUtils.save_map(world, target), 'Save copy failed'
assert unreal.EditorLoadingAndSavingUtils.load_map(target), 'Load copy failed'
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name() == target + '.Studio_YU7', world.get_path_name()
with (ROOT / 'DEV_HISTORY.md').open('a', encoding='utf-8') as log:
    log.write('\n### 03 · 当前地图副本\n\n- 编辑器实测原地图为 `/Game/Studios/Levels/Studio_White`，10 个 Actor，无未保存地图或内容。已用 UE Save Map 另存为 `/Game/YU7/Maps/Studio_YU7`，后续仅编辑副本。原地图 SHA256 已记录至 `ue_original_map_hash.json`。\n- 批处理通过现有 Python 编辑器插件执行，临时任务队列仅读取本工作区文件，不开启网络监听，结束后关闭。\n- 导入采用显式 FbxFactory，临时关闭本次会话的 Interchange FBX 路由并在完成/异常后还原，以保证法线和分件设置生效；项目配置不变。\n')
flag = unreal.SystemLibrary.get_console_variable_bool_value('Interchange.FeatureFlags.Import.FBX')
unreal.SystemLibrary.execute_console_command(world, 'Interchange.FeatureFlags.Import.FBX 0')
try:
    runpy.run_path(str(ROOT / 'art/YU7_UNREAL/import_into_unreal.py'), run_name='__main__')
finally:
    unreal.SystemLibrary.execute_console_command(world, 'Interchange.FeatureFlags.Import.FBX ' + ('1' if flag else '0'))
RESULT = {'map': world.get_path_name(), 'import': 'completed'}
