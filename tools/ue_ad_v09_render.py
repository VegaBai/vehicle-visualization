"""Versioned v09 native MRQ; optional per-job map/sequence diagnostics."""
import unreal,json,time
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
r=json.loads((O/'render_request.json').read_text(encoding='utf-8-sig'))
sub=unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem);assert not sub.is_rendering()
queue=unreal.new_object(unreal.MoviePipelineQueue)
cases=r.get('cases',[{'case':'Shot','map':D+'/Maps/Studio_YU7_TunnelFlow_AD_v09','sequence':D+'/Sequences/LS_YU7_TunnelFlow_AD_v09_12s','frames':r.get('frames')}])
assert len({c['map'] for c in cases})==1,'PIE executor renders the currently loaded map; use one map per run'
target_map=cases[0]['map']
current=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split('.')[0]
if current!=target_map:
    lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
    unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
    assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
    assert unreal.EditorLoadingAndSavingUtils.load_map(target_map)
for case in cases:
    clips=[(str(f),f,f+1) for f in case['frames']] if case.get('frames') is not None else [('Motion',0,288)]
    for label,start,end in clips:
        job=queue.allocate_new_job(unreal.MoviePipelineExecutorJob);job.job_name=r['name']+'_'+case['case']+'_'+label;job.author='VehicleStudio'
        job.map=unreal.SoftObjectPath(case['map']+'.'+case['map'].split('/')[-1]);job.sequence=unreal.SoftObjectPath(case['sequence']+'.'+case['sequence'].split('/')[-1])
        cfg=job.get_configuration();cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG).write_alpha=False
        output=cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        folder=R/'renders/YU7_TunnelFlow/ArtDirection_v09'/r['name']
        filename=r['name']+('_'+case['case'] if 'cases' in r else '')+'_{frame_number}'
        output.set_editor_properties({'output_directory':unreal.DirectoryPath(str(folder)),'file_name_format':filename,'output_resolution':unreal.IntPoint(r.get('width',1280),r.get('height',720)),'use_custom_frame_rate':True,'output_frame_rate':unreal.FrameRate(24,1),'use_custom_playback_range':True,'custom_start_frame':start,'custom_end_frame':end,'zero_pad_frame_numbers':4,'override_existing_output':False,'flush_disk_writes_per_shot':True})
        aa=cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting);aa.set_editor_properties({'spatial_sample_count':1,'temporal_sample_count':r.get('temporal',8),'override_anti_aliasing':True,'anti_aliasing_method':unreal.AntiAliasingMethod.AAM_NONE,'engine_warm_up_count':48,'render_warm_up_count':24,'render_warm_up_frames':True,'use_camera_cut_for_warm_up':False})
        cfg.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting).set_editor_properties({'cinematic_quality_settings':True,'use_lod_zero':True,'disable_hlods':True,'use_high_quality_shadows':True})
        cv=cfg.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
        for k,v in {'r.ScreenPercentage':100,'r.MotionBlurQuality':4,'r.MotionBlur.Amount':.3,'r.Shadow.Virtual.MaxPhysicalPages':8192,'r.Streaming.PoolSize':3000}.items():cv.add_or_update_console_variable(k,v)
        cfg.initialize_transient_settings()
        name='MRQ_'+job.job_name;assert not unreal.EditorAssetLibrary.does_asset_exist(D+'/RenderPresets/'+name)
        saved=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,D+'/RenderPresets',unreal.MoviePipelinePrimaryConfig,unreal.MoviePipelinePrimaryConfigFactory());saved.copy_from(cfg);unreal.EditorAssetLibrary.save_loaded_asset(saved)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
executor=unreal.MoviePipelinePIEExecutor();executor.set_is_rendering_offscreen(True)
state={'request':r,'started':time.time(),'status':'rendering','errors':[]};dest=O/(r['name']+'_status.json')
def save():dest.write_text(json.dumps(state,indent=2),encoding='utf-8')
def finished(executor,success):state.update(status='finished',success=success,duration_seconds=time.time()-state['started']);save()
def failed(executor,pipeline,is_fatal,error_text):state['errors'].append({'fatal':is_fatal,'text':str(error_text)});save()
executor.on_executor_finished_delegate.add_callable_unique(finished);executor.on_executor_errored_delegate.add_callable_unique(failed)
unreal._yu7_ad_render={'executor':executor,'queue':queue,'finished':finished,'failed':failed,'state':state};save();sub.render_queue_instance_with_executor_instance(queue,executor)
RESULT={'submitted':r}
