import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mp=D+'/Diagnostics/Maps/Diag_NoLane';sp=D+'/Diagnostics/Sequences/LS_Diag_NoLane'
assert not E.does_asset_exist(mp);assert E.duplicate_asset(D+'/Diagnostics/Maps/Diag_CleanBaseline',mp);assert E.save_asset(mp)
assert E.duplicate_asset(D+'/Diagnostics/Sequences/LS_Diag_CleanBaseline',sp);assert E.save_asset(sp)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0];assert unreal.EditorLoadingAndSavingUtils.load_map(mp)
actors={a.get_actor_label():a for a in A.get_all_level_actors()};seq=unreal.load_asset(sp)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq);unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).fix_actor_references();unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
actors['SEQ_YU7_TunnelFlow'].modify();actors['SEQ_YU7_TunnelFlow'].set_sequence(seq)
arch=actors['YU7_Tunnel_Architecture'];arch.modify()
c=next(c for c in arch.get_components_by_class(unreal.InstancedStaticMeshComponent) if c.get_name()=='Tunnel_Lane');c.modify();c.set_visibility(False);c.set_hidden_in_game(True)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(O/'render_request.json').write_text(json.dumps({'name':'Diagnosis_r03_NoLane','width':1280,'height':720,'temporal':8,'cases':[{'case':'NoLane','map':mp,'sequence':sp,'frames':[24,228]}]}),encoding='utf-8')
exec(compile((R/'tools/ue_ad_v09_render.py').read_text(),'render_lane','exec'))
