"""Targeted completion of v11's unfinished material after Noise pin discovery."""
import unreal,json
exec(compile(open('C:/github2/vehicle_visualization/tools/yu7_finish_v11_common.py').read(),'finish_common','exec'))
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
assert not (O/'prepared.json').exists()
seq=unreal.load_asset(SEQ);actors={a.get_actor_label():a for a in A.get_all_level_actors()}
original=unreal.load_asset('/Game/YU7/Cinematics/Materials/MI_Hero_MineralTeal')
scalars=['Metallic','BaseRoughness','ClearCoat','CoatRoughness','Specular','ColorFlop','FlakeStrength'];vectors=['PigmentColor','EdgeTint']
for k in scalars:FINISHES[-1][k]=0. if k=='FlakeStrength' else M.get_material_instance_scalar_parameter_value(original,k)
for k in vectors:
    v=M.get_material_instance_vector_parameter_value(original,k);FINISHES[-1][k]=[v.r,v.g,v.b]
mpc=unreal.load_asset(D+'/Materials/MPC_YU7_Finish_v11');assert mpc
paint=unreal.load_asset(D+'/Materials/M_YU7_Finish_v11');assert paint
M.delete_all_material_expressions(paint)
code=(R/'tools/ue_finish_v11_prepare.py').read_text()
code=code[code.index("paint.set_editor_properties"):].replace("link(pos,noise,'Position')","link(pos,noise,'World Position')")
exec(compile(code,'finish_v11_material_complete','exec'))
