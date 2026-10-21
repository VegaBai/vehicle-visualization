"""ONE-TIME native retiming plus finish parameter animation in isolated sequence."""
import unreal,json,bisect
exec(compile(open('C:/github2/vehicle_visualization/tools/yu7_finish_v11_common.py').read(),'finish_common','exec'))
E=unreal.EditorAssetLibrary
assert not (O/'sequence_applied.json').exists()
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
seq=unreal.load_asset(SEQ);assert seq and seq.get_playback_end()==288
seq.modify();records=[]
tracks=list(seq.get_tracks())+[t for b in seq.get_bindings() for t in b.get_tracks()]
for tr in tracks:
    for s in tr.get_sections():
        s.set_range(-48,TOTAL+49)
        for ch in s.get_all_channels():
            keys=ch.get_keys()
            if not keys:continue
            samples=sorted((k.get_time().frame_number.value+float(k.get_time().sub_frame),k.get_value()) for k in keys)
            times=[x[0] for x in samples]
            def value(t):
                j=bisect.bisect_right(times,t)
                if j==0:return samples[0][1]
                if j==len(samples):return samples[-1][1]
                a,x=samples[j-1];b,y=samples[j];return x+(y-x)*(t-a)/(b-a)
            vals=[(f,value(source_frame(f))) for f in range(-48,TOTAL+49)]
            for k in keys:ch.remove_key(k)
            for f,v in vals:ch.add_key(unreal.FrameNumber(f),v,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
            records.append({'track':tr.get_class().get_name(),'channel':ch.get_name(),'original_keys':len(samples),'new_keys':len(vals)})
seq.set_playback_end(TOTAL);seq.set_work_range_end(20.);seq.set_view_range_end(18.)
palette=json.loads((O/'palette.json').read_text())
mpc=unreal.load_asset(D+'/Materials/MPC_YU7_Finish_v11')
track=seq.add_track(unreal.MovieSceneMaterialParameterCollectionTrack);track.set_editor_property('mpc',mpc)
section=track.add_section();section.set_range(-48,TOTAL+49)
scalars=['Metallic','BaseRoughness','ClearCoat','CoatRoughness','Specular','ColorFlop','FlakeStrength'];vectors=['PigmentColor','EdgeTint']
cue=[]
for idx,p in enumerate(palette):
    start=-48 if idx==0 else p['frame']
    end=palette[idx+1]['frame']-6 if idx+1<len(palette) else TOTAL+48
    # Six-frame eased transitions, plateau values held between finish changes.
    points=[(start,p),(end,p)]
    if idx>0:
        prev=palette[idx-1]
        for j in range(1,6):
            u=j/6;u=u*u*(3-2*u);v={}
            for k in scalars:v[k]=prev[k]+(p[k]-prev[k])*u
            for k in vectors:v[k]=[a+(b-a)*u for a,b in zip(prev[k],p[k])]
            points.append((p['frame']-6+j,v))
    for f,v in points:
        for k in scalars:section.add_scalar_parameter_key(k,unreal.FrameNumber(f*1000),v[k],unreal.MovieSceneKeyInterpolation.LINEAR)
        for k in vectors:section.add_color_parameter_key(k,unreal.FrameNumber(f*1000),unreal.LinearColor(*v[k],1),unreal.MovieSceneKeyInterpolation.LINEAR)
    cue.append({'name':p['name'],'plateau_frames':[max(0,start),end],'transition_frames':6})
E.set_metadata_tag(seq,'Shot','18s / 432 frames / 24fps. Five finish showcase intro then original mineral teal. Native MPC finish track. Smoothly retimed original camera, drive, wheels, lights and ShotTime. No runtime Python/C++.')
assert E.save_loaded_asset(seq)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq);unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0);unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'fps':24,'frames':TOTAL,'retimed_channels':records,'finish_cues':cue,'source_frame_samples':{str(f):source_frame(f) for f in [0,24,144,156,168,180,192,240,366,431]},'original_effect_timing':'Preserved in ShotTime source seconds; original speed resumes at output8s/source2s.'}
(O/'sequence_applied.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
