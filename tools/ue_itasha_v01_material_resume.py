"""Targeted resume: copied map/imports exist; only unfinished material graph is rebuilt."""
import unreal,json,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_ITASHA/reports/v01';D='/Game/YU7/Itasha_v01';MAP=D+'/Maps/Studio_YU7_Itasha_v01'
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();V=unreal.VariantManagerLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()==MAP+'.Studio_YU7_Itasha_v01'
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
assert not any(n.startswith('YU7_Itasha') for n in actors)
assert not E.does_asset_exist(D+'/Materials/MI_Itasha_Rengoku')
textures={n:unreal.load_asset(D+'/Textures/T_Itasha_'+n) for n in ['rengoku','zenitsu','giyu']};assert all(textures.values())
mat=unreal.load_asset(D+'/Materials/M_Itasha_Artwork');assert mat
M.delete_all_material_expressions(mat)
code=(R/'tools/ue_itasha_v01_prepare.py').read_text(encoding='utf-8')
code=code[code.index("mat.set_editor_properties({'material_domain'"):]
exec(compile(code,'itasha_material_resume','exec'))
