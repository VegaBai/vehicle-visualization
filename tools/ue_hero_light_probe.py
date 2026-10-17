import unreal,json
from pathlib import Path
r=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in a.get_components_by_class(unreal.LightComponent):
        r.append({'actor':a.get_actor_label(),'actor_hidden':a.get_editor_property('hidden'),'component':c.get_name(),'class':c.get_class().get_name(),'intensity':c.intensity,'visible':c.visible,'hidden_in_game':c.hidden_in_game})
Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/hero/light_audit.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
RESULT=r
