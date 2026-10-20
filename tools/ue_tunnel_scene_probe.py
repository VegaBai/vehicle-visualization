import unreal,json
from pathlib import Path
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);E=unreal.EditorAssetLibrary
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
RESULT={'hero':hero.get_path_name(),'meshes':[{'name':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'visible':c.is_visible()} for c in hero.get_components_by_class(unreal.StaticMeshComponent)],'bps':[],'actors':[a.get_actor_label() for a in A.get_all_level_actors() if 'Tunnel' in a.get_actor_label()]}
S=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);L=unreal.SubobjectDataBlueprintFunctionLibrary
for p in E.list_assets('/Game/YU7/TunnelFlow/Blueprints'):
    bp=unreal.load_asset(p);RESULT['bps'].append({'path':p,'components':[str(L.get_object_for_blueprint(L.get_data(h),bp)) for h in S.k2_gather_subobject_data_for_blueprint(bp)]})
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/scene_failure_probe.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
