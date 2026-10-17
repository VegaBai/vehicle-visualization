"""Submit a saved native MRQ queue and retain async callbacks in the editor."""
import unreal,json,time
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/hero'
r=json.loads((OUT/'render_request.json').read_text(encoding='utf-8-sig'))
sub=unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem);assert not sub.is_rendering()
queue=unreal.new_object(unreal.MoviePipelineQueue)
job=queue.allocate_new_job(unreal.MoviePipelineExecutorJob);job.job_name=r['name'];job.author='VehicleStudio';job.comment='Mineral teal hero, original UE render'
job.map=unreal.SoftObjectPath('/Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero.Studio_YU7_MineralHero')
job.sequence=unreal.SoftObjectPath('/Game/YU7/Cinematics/Sequences/LS_YU7_MineralHero_5s.LS_YU7_MineralHero_5s')
cfg=job.get_configuration();cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
png=cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG);png.write_alpha=False
if r.get('exr'):cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_EXR)
output=cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
output.set_editor_properties({'output_directory':unreal.DirectoryPath(str(ROOT/r['directory'])),'file_name_format':r['name']+'_{frame_number}','output_resolution':unreal.IntPoint(r['width'],r['height']),'use_custom_frame_rate':True,'output_frame_rate':unreal.FrameRate(24,1),'use_custom_playback_range':True,'custom_start_frame':r.get('start',0),'custom_end_frame':r.get('end',120),'zero_pad_frame_numbers':4,'override_existing_output':False,'flush_disk_writes_per_shot':True})
output.set_editor_property('output_frame_step',r.get('step',1))
aa=cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
aa.set_editor_properties({'spatial_sample_count':r.get('spatial',1),'temporal_sample_count':r.get('temporal',8),'override_anti_aliasing':True,'anti_aliasing_method':unreal.AntiAliasingMethod.AAM_NONE,'engine_warm_up_count':64,'render_warm_up_count':32,'render_warm_up_frames':True,'use_camera_cut_for_warm_up':False})
game=cfg.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
game.set_editor_properties({'cinematic_quality_settings':True,'use_lod_zero':True,'disable_hlods':True,'use_high_quality_shadows':True})
cvars=cfg.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
for name,value in {'r.ScreenPercentage':100,'r.MotionBlurQuality':4,'r.MotionBlur.Amount':r.get('motion_blur',0.25),'r.Shadow.Virtual.MaxPhysicalPages':8192,'r.Streaming.PoolSize':3000}.items():cvars.add_or_update_console_variable(name,value)
cfg.initialize_transient_settings()
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools()
dest='/Game/YU7/Cinematics/RenderPresets/MRQ_'+r['name']
assert not E.does_asset_exist(dest),'Choose a new render name to preserve prior settings'
saved=T.create_asset('MRQ_'+r['name'],'/Game/YU7/Cinematics/RenderPresets',unreal.MoviePipelinePrimaryConfig,unreal.MoviePipelinePrimaryConfigFactory())
saved.copy_from(cfg);E.save_loaded_asset(saved)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
executor=unreal.MoviePipelinePIEExecutor();executor.set_is_rendering_offscreen(True)
state={'name':r['name'],'request':r,'started':time.time(),'status':'rendering','errors':[],'preset':saved.get_path_name()}
status_path=OUT/(r['name']+'_status.json')
def save():status_path.write_text(json.dumps(state,indent=2),encoding='utf-8')
def finished(executor,success):
    state.update({'status':'finished','success':success,'finished':time.time(),'duration_seconds':time.time()-state['started']});save()
def failed(executor,pipeline,is_fatal,error_text):
    state['errors'].append({'fatal':is_fatal,'text':str(error_text)});save()
executor.on_executor_finished_delegate.add_callable_unique(finished)
executor.on_executor_errored_delegate.add_callable_unique(failed)
unreal._yu7_hero_render={'executor':executor,'queue':queue,'finished':finished,'failed':failed,'state':state}
save()
sub.render_queue_instance_with_executor_instance(queue,executor)
RESULT={'submitted':r['name'],'preset':saved.get_path_name()}
