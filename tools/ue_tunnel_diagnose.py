import unreal,json
from pathlib import Path
D='/Game/YU7/TunnelFlow';E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();mpc=unreal.load_asset(D+'/Materials/MPC_TunnelFlow');seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_12s')
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq);unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(228)
RESULT={'mpc_default':str(mpc.get_scalar_parameter_default_value('ShotTime')),'brightness':unreal.MaterialEditingLibrary.get_material_default_scalar_parameter_value(unreal.load_asset(D+'/Materials/M_TunnelGrid'),'Brightness'),'mpc_value':unreal.MaterialLibrary.get_scalar_parameter_value(world,mpc,'ShotTime'),'tracks':[],'effects':[],'shader_nodes':[]}
for tr in seq.get_tracks():
    if isinstance(tr,unreal.MovieSceneMaterialParameterCollectionTrack):
        RESULT['tracks'].append({'mpc':str(tr.get_editor_property('mpc')),'sections':[{'channels':[{'name':str(c.channel_name),'keys':[{'time':str(k.get_time()),'value':k.get_value()} for k in c.get_keys()]} for c in s.get_all_channels()]} for s in tr.get_sections()]})
for a in A.get_all_level_actors():
    if a.get_actor_label().startswith('YU7_BodyQuad') or a.get_actor_label() in ['YU7_Tunnel_SurfaceFlow','YU7_Tunnel_WorldWake']:
        c=a.static_mesh_component;RESULT['effects'].append({'label':a.get_actor_label(),'transform':str(a.get_actor_transform()),'mesh':str(c.static_mesh),'material':str(c.get_material(0)),'visible':c.is_visible(),'hidden_in_game':c.get_editor_property('hidden_in_game'),'bounds':str(c.get_local_bounds())})
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/diagnose_v01.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
