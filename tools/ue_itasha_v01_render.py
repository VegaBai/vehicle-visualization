"""Render requested native camera stills with a saved, selected itasha/paint pair."""
import unreal, json, math, time
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_ITASHA/reports/v01';D='/Game/YU7/Itasha_v01';MAP=D+'/Maps/Studio_YU7_Itasha_v01'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
r=json.loads((O/'render_request.json').read_text(encoding='utf-8-sig'))
sub=unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem);assert not sub.is_rendering()
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()==MAP+'.Studio_YU7_Itasha_v01'
actors={a.get_actor_label():a for a in A.get_all_level_actors()};manager=actors['YU7_ItashaOptions']
assert manager.switch_on_variant_by_name('Itasha',r['itasha'])
assert manager.switch_on_variant_by_name('Paint',r['paint'])
views={'Side':((0,1030,170),(0,0,72),55),'Beauty':((-660,990,280),(0,0,73),55),'Right':((0,-1030,170),(0,0,72),55),'Hood':((-550,330,570),(-120,0,80),55)}
sequences={}
for name in r['views']:
    path=D+'/Sequences/LS_Itasha_'+name
    if E.does_asset_exist(path):seq=unreal.load_asset(path)
    else:
        loc,target,lens=views[name];loc=unreal.Vector(*loc);rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(*target))
        camera=A.spawn_actor_from_class(unreal.CineCameraActor,loc,rot);camera.set_actor_label('CAM_Itasha_'+name);camera.set_folder_path('YU7/Itasha/Cameras')
        c=camera.get_cine_camera_component();film=c.filmback;film.sensor_width=36;film.sensor_height=20.25;c.set_editor_property('filmback',film)
        c.set_editor_properties({'current_focal_length':lens,'current_aperture':8.})
        focus=c.focus_settings;focus.focus_method=unreal.CameraFocusMethod.DISABLE;c.set_editor_property('focus_settings',focus)
        seq=T.create_asset('LS_Itasha_'+name,D+'/Sequences',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());seq.set_display_rate(unreal.FrameRate(24,1));seq.set_playback_start(0);seq.set_playback_end(24)
        binding=seq.add_possessable(camera);cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(-48,48);cut.set_camera_binding_id(seq.get_binding_id(binding))
        E.set_metadata_tag(seq,'Attribution',(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip());assert E.save_loaded_asset(seq)
    sequences[name]=seq
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
queue=unreal.new_object(unreal.MoviePipelineQueue)
presets=[]
for name,seq in sequences.items():
    job=queue.allocate_new_job(unreal.MoviePipelineExecutorJob);job.job_name=r['name']+'_'+name;job.author='VehicleStudio';job.map=unreal.SoftObjectPath(MAP+'.Studio_YU7_Itasha_v01');job.sequence=unreal.SoftObjectPath(seq.get_path_name())
    cfg=job.get_configuration();cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    png=cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG);png.write_alpha=False
    output=cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
    output.set_editor_properties({'output_directory':unreal.DirectoryPath(str(R/'renders/YU7_Itasha_v01'/r['name'])),'file_name_format':job.job_name+'_{frame_number}','output_resolution':unreal.IntPoint(r.get('width',1920),r.get('height',1080)),'use_custom_frame_rate':True,'output_frame_rate':unreal.FrameRate(24,1),'use_custom_playback_range':True,'custom_start_frame':8,'custom_end_frame':9,'zero_pad_frame_numbers':4,'override_existing_output':False,'flush_disk_writes_per_shot':True})
    aa=cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting);aa.set_editor_properties({'spatial_sample_count':1,'temporal_sample_count':8,'override_anti_aliasing':True,'anti_aliasing_method':unreal.AntiAliasingMethod.AAM_NONE,'engine_warm_up_count':48,'render_warm_up_count':32,'render_warm_up_frames':True,'use_camera_cut_for_warm_up':False})
    game=cfg.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting);game.set_editor_properties({'cinematic_quality_settings':True,'use_lod_zero':True,'disable_hlods':True,'use_high_quality_shadows':True})
    cv=cfg.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
    for k,v in {'r.ScreenPercentage':100,'r.MotionBlurQuality':0,'r.Shadow.Virtual.MaxPhysicalPages':8192,'r.Streaming.PoolSize':3000}.items():cv.add_or_update_console_variable(k,v)
    cfg.initialize_transient_settings();pn='MRQ_'+job.job_name;assert not E.does_asset_exist(D+'/RenderPresets/'+pn)
    saved=T.create_asset(pn,D+'/RenderPresets',unreal.MoviePipelinePrimaryConfig,unreal.MoviePipelinePrimaryConfigFactory());saved.copy_from(cfg);assert E.save_loaded_asset(saved);presets.append(saved.get_path_name())
executor=unreal.MoviePipelinePIEExecutor();executor.set_is_rendering_offscreen(True)
state={'name':r['name'],'request':r,'status':'rendering','started':time.time(),'errors':[],'presets':presets};path=O/(r['name']+'_status.json')
def save():path.write_text(json.dumps(state,indent=2),encoding='utf-8')
def finished(executor,success):
    state.update({'status':'finished','success':success,'duration_seconds':time.time()-state['started']});save()
def failed(executor,pipeline,is_fatal,error_text):state['errors'].append({'fatal':is_fatal,'text':str(error_text)});save()
executor.on_executor_finished_delegate.add_callable_unique(finished);executor.on_executor_errored_delegate.add_callable_unique(failed)
unreal._itasha_render={'executor':executor,'queue':queue,'finished':finished,'failed':failed,'state':state};save()
sub.render_queue_instance_with_executor_instance(queue,executor)
RESULT={'submitted':r,'presets':presets}
