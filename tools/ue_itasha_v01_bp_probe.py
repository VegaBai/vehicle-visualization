import unreal,json
from pathlib import Path
bp=unreal.load_asset('/Game/YU7/Itasha_v01/Blueprints/BP_YU7_ItashaVehicle');sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
rows=[]
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    data=lib.get_data(h);c=lib.get_object_for_blueprint(data,bp);o=lib.get_object(data)
    rows.append({'blueprint_object':c.get_path_name() if c else None,'class':c.get_class().get_name() if c else None,'object':o.get_path_name() if o else None,'object_class':o.get_class().get_name() if o else None})
RESULT={'count':len(rows),'rows':rows};Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01/bp_probe.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
