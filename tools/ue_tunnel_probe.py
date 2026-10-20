import unreal,json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports');OUT.mkdir(parents=True,exist_ok=True)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
RESULT={'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'api':{},'actors':[]}
for name in ['MovieSceneMaterialParameterCollectionTrack','MovieSceneParameterSection','MaterialParameterCollection','CollectionScalarParameter','MaterialExpressionCollectionParameter','MaterialExpressionTransformPosition','MaterialExpressionCustom','CustomInput','MovieSceneFloatTrack','LevelSequenceActor']:
    cls=getattr(unreal,name,None)
    RESULT['api'][name]={'doc':str(cls.__doc__) if cls else None,'methods':{n:str(getattr(cls,n).__doc__) for n in dir(cls or object) if any(k in n for k in ['scalar_parameter','collection','sequence','playback','parameter_key'])}}
for a in A.get_all_level_actors():
    row={'label':a.get_actor_label(),'class':a.get_class().get_name(),'transform':str(a.get_actor_transform())}
    if a.get_actor_label()=='YU7_Hero':
        row['meshes']=[{'component':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'relative':str(c.get_relative_transform()),'bounds':str(c.get_local_bounds())} for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh]
    RESULT['actors'].append(row)
(OUT/'probe.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
