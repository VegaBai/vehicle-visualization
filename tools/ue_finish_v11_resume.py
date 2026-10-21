"""Targeted recovery: saved sequence exists; no new map/material was saved."""
import unreal,json
exec(compile(open('C:/github2/vehicle_visualization/tools/yu7_finish_v11_common.py').read(),'finish_common','exec'))
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not E.does_asset_exist(MAP)
assert not E.does_directory_exist(D+'/Materials')
seq=unreal.load_asset(SEQ);assert seq and seq.get_playback_end()==288
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/YU7/TunnelFlow/RoofSmooth_v10/Maps/')
assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(MAP)
code=(R/'tools/ue_finish_v11_prepare.py').read_text()
code=code[code.index('actors={a.get_actor_label()'):]
exec(compile(code,'finish_v11_after_saved_map','exec'))
