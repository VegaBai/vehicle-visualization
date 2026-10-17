import json
from pathlib import Path
import unreal

OUT = Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports')
sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = sub.get_editor_world()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
report = {
    'engine': unreal.SystemLibrary.get_engine_version(),
    'project': unreal.Paths.get_project_file_path(),
    'world': world.get_path_name(),
    'dirty_maps': [p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
    'dirty_content': [p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],
    'actors': [],
}
for a in actors:
    report['actors'].append({'name': a.get_name(), 'label': a.get_actor_label(), 'class': a.get_class().get_path_name(), 'location': str(a.get_actor_location()), 'rotation': str(a.get_actor_rotation()), 'scale': str(a.get_actor_scale3d()), 'bounds': str(a.get_actor_bounds(False)), 'components': [{'name': c.get_name(), 'class': c.get_class().get_name()} for c in a.get_components_by_class(unreal.ActorComponent)]})
OUT.joinpath('ue_before.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
names = ['EditorLevelLibrary','LevelEditorSubsystem','EditorLoadingAndSavingUtils','SubobjectDataSubsystem','SubobjectDataBlueprintFunctionLibrary','AddNewSubobjectParams','BlueprintFactory','BlueprintEditorLibrary','StaticMeshEditorSubsystem','GeometryScript_AssetUtils','GeometryScript_Normals','GeometryScript_MeshQueries','GeometryScript_MeshReadWrite','GeometryScript_UVs','AutomationLibrary','EditorAssetLibrary']
docs = {}
for name in names:
    cls = getattr(unreal, name, None)
    docs[name] = {'doc': str(getattr(cls, '__doc__', 'unavailable')), 'methods': {x: str(getattr(cls, x).__doc__) for x in dir(cls) if not x.startswith('_') and any(t in x for t in ['save','duplicate','subobject','blueprint','mesh','normal','uv','screenshot','viewport','camera'])}} if cls else None
OUT.joinpath('ue_api.json').write_text(json.dumps(docs, indent=2), encoding='utf-8')
RESULT = report
