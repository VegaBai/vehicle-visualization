"""Versioned clean lighting render at unchanged v08 cameras for comparison."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mp=D+'/Diagnostics/Maps/Diag_Lighting_r06';sp=D+'/Diagnostics/Sequences/LS_Diag_Lighting_r06'
assert not E.does_asset_exist(mp)
assert E.duplicate_asset(D+'/Maps/Studio_YU7_TunnelFlow_AD_v09',mp);assert E.save_asset(mp)
assert E.duplicate_asset(D+'/Sequences/LS_YU7_TunnelFlow_AD_v09_12s',sp);assert E.save_asset(sp)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0];assert unreal.EditorLoadingAndSavingUtils.load_map(mp)
actors={a.get_actor_label():a for a in A.get_all_level_actors()};seq=unreal.load_asset(sp)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq);unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).fix_actor_references();unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
actors['SEQ_YU7_TunnelFlow'].modify();actors['SEQ_YU7_TunnelFlow'].set_sequence(seq)
for label,a in actors.items():
    if label.startswith('YU7_BodyQuad_') or label in ['YU7_Tunnel_SurfaceFlow','YU7_Tunnel_RoofAirflow','YU7_Tunnel_WorldWake']:
        a.modify();a.set_actor_hidden_in_game(True)
    if label.startswith('YU7_Tunnel_ScanLight_'):a.modify();a.point_light_component.modify();a.point_light_component.set_visibility(False)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(O/'render_request.json').write_text(json.dumps({'name':'Lighting_r06_1080p','width':1920,'height':1080,'temporal':8,'cases':[{'case':'Clean','map':mp,'sequence':sp,'frames':[24,228,276]}]}),encoding='utf-8')
exec(compile((R/'tools/ue_ad_v09_render.py').read_text(),'render_clean','exec'))
