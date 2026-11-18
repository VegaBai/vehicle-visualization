"""Resume only the partial v12 preparation after template-name probe failure."""
from pathlib import Path
R=Path('C:/github2/vehicle_visualization')
code=(R/'tools/ue_v12_prepare.py').read_text(encoding='utf-8-sig')
code=code.replace("assert not E.does_directory_exist(D),'One time only; inspect partial state on failure'","assert E.does_directory_exist(D)")
code=code.replace("assert world.get_path_name().startswith('/Game/YU7/TunnelFlow/FinishShowcase_v11/Maps/')","""lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(MAP)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith(D+'/Maps/')""")
code=code.replace('assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)','')
code=code.replace("seq=E.duplicate_asset('/Game/YU7/TunnelFlow/FinishShowcase_v11/Sequences/LS_YU7_FinishShowcase_v11_18s',SEQ);assert seq","seq=unreal.load_asset(SEQ);assert seq")
code=code.replace("bp=E.duplicate_asset('/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7',D+'/Blueprints/BP_YU7_ItashaFilm_v12');assert bp","bp=unreal.load_asset(D+'/Blueprints/BP_YU7_ItashaFilm_v12');assert bp")
exec(compile(code,'v12_targeted_resume','exec'))
