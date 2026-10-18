"""Render a study request with native MRQ; retain completion evidence."""
import unreal,json,time
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports';DEST='/Game/YU7/WireframeStudy'
r=json.loads((OUT/'render_request.json').read_text(encoding='utf-8-sig'))
sub=unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem);assert not sub.is_rendering()
queue=unreal.new_object(unreal.MoviePipelineQueue)
for view in r.get('views',['Overview','Detail']):
    job=queue.allocate_new_job(unreal.MoviePipelineExecutorJob);job.job_name=r['name']+'_'+view;job.author='VehicleStudio';job.comment='Original UE surface quad study render'
    job.map=unreal.SoftObjectPath(DEST+'/Maps/Studio_YU7_QuadStudy.Studio_YU7_QuadStudy');job.sequence=unreal.SoftObjectPath(DEST+'/Sequences/LS_YU7_Quad_'+view+'.LS_YU7_Quad_'+view)
    cfg=job.get_configuration();cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG).write_alpha=False
    output=cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    output.set_editor_properties({'output_directory':unreal.DirectoryPath(str(ROOT/'renders/YU7_WireframeStudy'/r['name'])),'file_name_format':job.job_name+'_{frame_number}','output_resolution':unreal.IntPoint(r.get('width',1920),r.get('height',1080)),'use_custom_frame_rate':True,'output_frame_rate':unreal.FrameRate(24,1),'use_custom_playback_range':True,'custom_start_frame':0,'custom_end_frame':1,'zero_pad_frame_numbers':4,'override_existing_output':False,'flush_disk_writes_per_shot':True})
    aa=cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting);aa.set_editor_properties({'spatial_sample_count':r.get('samples',16),'temporal_sample_count':1,'override_anti_aliasing':True,'anti_aliasing_method':unreal.AntiAliasingMethod.AAM_NONE,'engine_warm_up_count':64,'render_warm_up_count':32,'render_warm_up_frames':True,'use_camera_cut_for_warm_up':False})
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting).set_editor_properties({'cinematic_quality_settings':True,'use_lod_zero':True,'disable_hlods':True,'use_high_quality_shadows':True})
    cv=cfg.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
    for k,v in {'r.ScreenPercentage':100,'r.MotionBlurQuality':0,'r.MotionBlur.Amount':0,'r.Shadow.Virtual.MaxPhysicalPages':8192,'r.Streaming.PoolSize':3000}.items():cv.add_or_update_console_variable(k,v)
    cfg.initialize_transient_settings()
    path=DEST+'/RenderPresets/MRQ_'+job.job_name;assert not unreal.EditorAssetLibrary.does_asset_exist(path)
    saved=unreal.AssetToolsHelpers.get_asset_tools().create_asset('MRQ_'+job.job_name,DEST+'/RenderPresets',unreal.MoviePipelinePrimaryConfig,unreal.MoviePipelinePrimaryConfigFactory());saved.copy_from(cfg);unreal.EditorAssetLibrary.save_loaded_asset(saved)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
executor=unreal.MoviePipelinePIEExecutor();executor.set_is_rendering_offscreen(True)
state={'request':r,'started':time.time(),'status':'rendering','errors':[]};dest=OUT/(r['name']+'_status.json')
def save():dest.write_text(json.dumps(state,indent=2),encoding='utf-8')
def finished(executor,success):state.update(status='finished',success=success,duration_seconds=time.time()-state['started']);save()
def failed(executor,pipeline,is_fatal,error_text):state['errors'].append({'fatal':is_fatal,'text':str(error_text)});save()
executor.on_executor_finished_delegate.add_callable_unique(finished);executor.on_executor_errored_delegate.add_callable_unique(failed)
unreal._yu7_quad_render={'executor':executor,'queue':queue,'finished':finished,'failed':failed,'state':state};save();sub.render_queue_instance_with_executor_instance(queue,executor)
RESULT={'submitted':r}
