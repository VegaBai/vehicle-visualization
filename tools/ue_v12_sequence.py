"""One-time native 24s retiming, finish animation and decal visibility tracks."""
import unreal,json,bisect
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12';D='/Game/YU7/TunnelFlow/ItashaShowcase_v12'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
assert not (O/'sequence_applied.json').exists()
E=unreal.EditorAssetLibrary;L=unreal.LevelSequenceEditorBlueprintLibrary
seq=unreal.load_asset(D+'/Sequences/LS_YU7_ItashaShowcase_v12_24s');assert seq.get_playback_end()==432
seq.modify();records=[]
paint_collection=unreal.load_asset('/Game/YU7/TunnelFlow/FinishShowcase_v11/Materials/MPC_YU7_Finish_v11')
for tr in list(seq.get_tracks()):
    if isinstance(tr,unreal.MovieSceneMaterialParameterCollectionTrack) and tr.get_editor_property('mpc')==paint_collection:seq.remove_track(tr)
def source_frame(f):return f*.5 if f<=288 else f-144
for tr in list(seq.get_tracks())+[t for b in seq.get_bindings() for t in b.get_tracks()]:
    for section in tr.get_sections():
        section.set_range(-48,625)
        for ch in section.get_all_channels():
            keys=ch.get_keys()
            if not keys:continue
            samples=sorted((k.get_time().frame_number.value+float(k.get_time().sub_frame),k.get_value()) for k in keys)
            assert isinstance(samples[0][1],(float,int)),(ch.get_name(),type(samples[0][1]))
            times=[x[0] for x in samples]
            def value(t):
                j=bisect.bisect_right(times,t)
                if j==0:return samples[0][1]
                if j==len(samples):return samples[-1][1]
                a,x=samples[j-1];b,y=samples[j];return x+(y-x)*(t-a)/(b-a)
            values=[(f,value(source_frame(f))) for f in range(-48,625)]
            for k in keys:ch.remove_key(k)
            for f,v in values:ch.add_key(unreal.FrameNumber(f),v,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
            records.append(str(ch.get_name()))
seq.set_playback_end(576);seq.set_work_range_end(26.);seq.set_view_range_end(24.)
palette=json.loads((R/'art/YU7_TUNNEL_FLOW/reports/finish_v11/palette.json').read_text())
cues=[dict(p) for p in palette[:5]]
for index,frame,name in [(2,150,'Rengoku | Pearl White'),(3,198,'Zenitsu | Graphite'),(5,246,'Giyu | Mineral Teal')]:
    p=dict(palette[index]);p.update(frame=frame,name=name);cues.append(p)
track=seq.add_track(unreal.MovieSceneMaterialParameterCollectionTrack);track.set_editor_property('mpc',paint_collection)
section=track.add_section();section.set_range(-48,625)
scalars=['Metallic','BaseRoughness','ClearCoat','CoatRoughness','Specular','ColorFlop','FlakeStrength'];vectors=['PigmentColor','EdgeTint']
for idx,p in enumerate(cues):
    start=-48 if idx==0 else p['frame'];end=cues[idx+1]['frame']-6 if idx+1<len(cues) else 624
    points=[(start,p),(end,p)]
    if idx:
        prev=cues[idx-1]
        for j in range(1,6):
            u=j/6;u=u*u*(3-2*u);v={k:prev[k]+(p[k]-prev[k])*u for k in scalars}
            v.update({k:[a+(b-a)*u for a,b in zip(prev[k],p[k])] for k in vectors});points.append((p['frame']-6+j,v))
    for f,v in points:
        for k in scalars:section.add_scalar_parameter_key(k,unreal.FrameNumber(f*1000),v[k],unreal.MovieSceneKeyInterpolation.LINEAR)
        for k in vectors:section.add_color_parameter_key(k,unreal.FrameNumber(f*1000),unreal.LinearColor(*v[k],1),unreal.MovieSceneKeyInterpolation.LINEAR)
visibility=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(a,unreal.DecalActor):continue
    name=next(n for n in ['Rengoku','Zenitsu','Giyu'] if '_'+n+'_v12' in a.get_actor_label())
    start,end={'Rengoku':(150,192),'Zenitsu':(198,240),'Giyu':(246,288)}[name]
    binding=seq.add_possessable(a);track=binding.add_track(unreal.MovieSceneVisibilityTrack)
    track.set_property_name_and_path('bHidden','bHidden');s=track.add_section();s.set_range(-48,625);ch=s.get_all_channels()[0]
    # Visibility track bool means visible, despite the underlying bHidden property.
    for f,val in [(-48,False),(start,True),(end,False)]:ch.add_key(unreal.FrameNumber(f),val)
    visibility.append({'actor':a.get_actor_label(),'visible_frames':[start,end-1]})
assert len(visibility)==15
E.set_metadata_tag(seq,'Shot','24s / 576 frames / 24fps. Five paint stages, three 2s itasha/paint stages, original airflow/grid finish. Native Sequencer only.')
assert E.save_loaded_asset(seq)
L.open_level_sequence(seq);L.set_current_time(0);L.close_level_sequence()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'frames':576,'fps':24,'retimed_channels':records,'palette':cues,'visibility':visibility,'source_v11_frame_mapping':'f/2 through frame288; f-144 thereafter','status':'authored; PIE and visual validation pending'}
(O/'sequence_applied.json').write_text(json.dumps(RESULT,indent=2))
