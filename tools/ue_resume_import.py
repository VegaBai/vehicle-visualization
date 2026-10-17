import runpy
from pathlib import Path
import unreal
ROOT = Path('C:/github2/vehicle_visualization')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name() == '/Game/YU7/Maps/Studio_YU7.Studio_YU7'
flag = unreal.SystemLibrary.get_console_variable_bool_value('Interchange.FeatureFlags.Import.FBX')
unreal.SystemLibrary.execute_console_command(world, 'Interchange.FeatureFlags.Import.FBX 0')
try:
    module = runpy.run_path(str(ROOT / 'art/YU7_UNREAL/import_into_unreal.py'), run_name='yu7_import')
    module['run'](resume=True)
finally:
    unreal.SystemLibrary.execute_console_command(world, 'Interchange.FeatureFlags.Import.FBX ' + ('1' if flag else '0'))
RESULT = {'map': world.get_path_name(), 'import': 'completed'}
