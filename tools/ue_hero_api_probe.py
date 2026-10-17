import unreal,json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/hero')
names=['MovieSceneSequenceExtensions.get_binding_id','MovieSceneSequenceExtensions.add_possessable','MovieSceneSectionExtensions.get_channels','MovieSceneScriptingDoubleChannel.add_key','MovieSceneCameraCutSection.set_camera_binding_id','MoviePipelineQueueSubsystem.render_queue_with_executor_instance','MoviePipelineExecutorBase.on_executor_finished_delegate','MoviePipelinePIEExecutor.on_individual_job_finished_delegate','MoviePipelineConsoleVariableSetting.add_or_update_console_variable','MoviePipelinePrimaryConfig','MoviePipelineDeferredPassBase','MoviePipelinePathTracer','MoviePipelineGameOverrideSetting','MoviePipelineImageSequenceOutput_EXR','MoviePipelineImageSequenceOutput_PNG','MoviePipelineQueue','MoviePipelineQueue.copy_from','MoviePipelineExecutorJob','MovieSceneScriptingKey','MovieSceneScriptingDoubleKey','MovieSceneSectionExtensions.set_range','MovieScene3DTransformSection','MovieSceneObjectBindingID','LevelVariantSetsActor.set_level_variant_sets']
r={}
for n in names:
    try:
        v=unreal
        for part in n.split('.'):v=getattr(v,part)
        r[n]=getattr(v,'__doc__',None)
    except Exception as e:r[n]=str(e)
(OUT/'render_api.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
RESULT={'probed':len(r)}
