import unreal,json
from pathlib import Path
O=Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/itasha_v12')
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
rows=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not a.get_actor_label().startswith('YU7_Tunnel_Wheel_'):continue
    bp=unreal.load_asset(a.get_class().get_path_name().split('.')[0]);templates=[]
    for h in sub.k2_gather_subobject_data_for_blueprint(bp):
        c=lib.get_object_for_blueprint(lib.get_data(h),bp)
        if isinstance(c,unreal.PrimitiveComponent):templates.append({'name':c.get_name(),'receives':c.get_editor_property('receives_decals')})
    rows.append({'actor':a.get_actor_label(),'class':a.get_class().get_path_name(),'components':[{'name':c.get_name(),'receives':c.get_editor_property('receives_decals')} for c in a.get_components_by_class(unreal.PrimitiveComponent)],'templates':templates})
RESULT=rows;(O/'wheel_probe.json').write_text(json.dumps(rows,indent=2))
