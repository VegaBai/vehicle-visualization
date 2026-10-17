"""Read-only editorial scene/API inventory for the mineral-teal hero shot."""
import unreal, json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/hero'); OUT.mkdir(parents=True,exist_ok=True)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def props(obj,names):
    result={}
    for n in names:
        try: result[n]=str(obj.get_editor_property(n))
        except Exception as e: result[n]=str(e)
    return result
report={'world':world.get_path_name(),'dirty_maps':[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'actors':[]}
for a in A.get_all_level_actors():
    row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation())}
    if isinstance(a,unreal.Light): row['light']=props(a.get_component_by_class(unreal.LightComponent),['intensity','specular_scale','cast_shadows','indirect_lighting_intensity','source_width','source_height','source_texture','temperature','visible','hidden_in_game'])
    if isinstance(a,unreal.PostProcessVolume): row['post']=props(a.settings,['auto_exposure_min_brightness','auto_exposure_max_brightness','auto_exposure_bias','lumen_scene_lighting_quality','lumen_final_gather_quality','lumen_reflection_quality','lumen_front_layer_translucency_reflections'])
    if isinstance(a,unreal.CineCameraActor): row['camera']=props(a.get_cine_camera_component(),['current_focal_length','current_aperture','filmback','focus_settings'])
    report['actors'].append(row)
api={}
for name in ['MovieSceneSequenceExtensions','MovieSceneSectionExtensions','MovieSceneScriptingDoubleChannel','LevelSequence','MoviePipelineQueueSubsystem','MoviePipelinePIEExecutor','MoviePipelineOutputSetting','MoviePipelineAntiAliasingSetting','MoviePipelineDeferredPassBase','MoviePipelinePathTracer','MoviePipelineConsoleVariableSetting','MoviePipelineGameOverrideSetting','MovieSceneCameraCutSection','MovieScene3DTransformSection','PluginBlueprintLibrary','EditorLoadingAndSavingUtils','LevelSequenceEditorBlueprintLibrary']:
    obj=getattr(unreal,name,None);api[name]={'doc':getattr(obj,'__doc__',None),'members':[x for x in dir(obj) if not x.startswith('_')] if obj else []}
(OUT/'before.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/'api.json').write_text(json.dumps(api,indent=2),encoding='utf-8')
RESULT={'world':report['world'],'dirty_maps':report['dirty_maps'],'dirty_content':report['dirty_content'],'actors':len(report['actors']),'sequencer_scripting':hasattr(unreal,'MovieSceneSequenceExtensions')}
