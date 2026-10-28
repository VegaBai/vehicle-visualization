"""Read serialized wrapper/reference state after a safe reload."""
import unreal,json
from pathlib import Path
D='/Game/YU7/Itasha_v01'
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=next(x for x in A.get_all_level_actors() if x.get_actor_label()=='YU7_ItashaOptions')
lvs=unreal.load_asset(D+'/Variants/LVS_YU7_Itasha_v01')
cdo=unreal.get_default_object(a.get_class())
def ref(x):
    v=x.get_level_variant_sets(True)
    return v.get_path_name() if v else None
RESULT={'instance_ref':ref(a),'class_ref':ref(cdo),'loaded_ref':lvs.get_path_name(),'sets':[str(lvs.get_variant_set(i).get_display_text()) for i in range(lvs.get_num_variant_sets())]}
Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01/reload_probe.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
