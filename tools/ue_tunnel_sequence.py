"""Deterministic 12 s native Sequencer: drive, wheels, dolly, light and MPC."""
import unreal,json,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not E.does_asset_exist(D+'/Sequences/LS_YU7_TunnelFlow_12s')
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero'];camera=actors['CAM_YU7_TunnelFlow']
seq=T.create_asset('LS_YU7_TunnelFlow_12s',D+'/Sequences',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());seq.set_display_rate(unreal.FrameRate(24,1));seq.set_tick_resolution_directly(unreal.FrameRate(24000,1));seq.set_playback_start(0);seq.set_playback_end(288);seq.set_work_range_start(-2.);seq.set_work_range_end(14.);seq.set_view_range_start(0.);seq.set_view_range_end(12.)
frames=list(range(-48,337,2));records={}
def curve(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:u=(t-a)/(b-a);u=u*u*(3-2*u);return x+(y-x)*u
    return keys[-1][1]
def transform(a,fn):
    binding=seq.add_possessable(a);track=binding.add_track(unreal.MovieScene3DTransformTrack);section=track.add_section();section.set_range(-48,337);section.set_editor_property('use_quaternion_interpolation',False)
    channels=section.get_all_channels();assert len(channels)==9
    for f in frames:
        loc,rot=fn(f/24.)
        for c,v in zip(channels,[*loc,rot[2],rot[0],rot[1],1.,1.,1.]):c.add_key(unreal.FrameNumber(f),v,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    records[a.get_actor_label()]={'keys':len(frames),'section':[-48,337]};return binding
hero_binding=transform(hero,lambda t:((-1500*t,0,0),(0,180,0)))
wheel_report=json.loads((O/'scene_v01.json').read_text())['wheels']
for w in wheel_report:transform(actors[w['actor']],lambda t,w=w:(w['local_center'],(-math.degrees(1500*t/38.2397),0,0)))
def camera_at(t):
    angle=math.radians(curve(t,[(0,35),(4.5,51),(9.1,83),(12,115)]));radius=curve(t,[(0,890),(4.5,785),(8.5,790),(10,900),(12,1060)])
    z=curve(t,[(0,110),(4.5,125),(8.5,145),(12,125)])
    loc=unreal.Vector(-1500*t-radius*math.cos(angle),radius*math.sin(angle),z)
    target=unreal.Vector(-1500*t+curve(t,[(0,0),(9.5,0),(12,-70)]),0,77)
    rot=unreal.MathLibrary.find_look_at_rotation(loc,target);return (loc.x,loc.y,loc.z),(rot.pitch,rot.yaw,rot.roll)
camera_binding=transform(camera,camera_at)
cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(-48,337);cut.set_camera_binding_id(seq.get_binding_id(camera_binding))
mpc=unreal.load_asset(D+'/Materials/MPC_TunnelFlow');track=seq.add_track(unreal.MovieSceneMaterialParameterCollectionTrack);track.set_editor_property('mpc',mpc);section=track.add_section();section.set_range(-48,337)
# Native parameter-section APIs consume tick-resolution frame numbers.
for f in [-48,0,288,336]:section.add_scalar_parameter_key('ShotTime',unreal.FrameNumber(f*1000),f/24.,unreal.MovieSceneKeyInterpolation.LINEAR)
def scan(t):return max(0,min(1,(t-1.5)/2.8 if t<4.6 else (t-4.7)/3.95))
for label,sign in [('L',-1),('R',1)]:
    a=actors['YU7_Tunnel_ScanLight_'+label]
    bind=transform(a,lambda t,sign=sign:((250-500*scan(t),sign*106,105),(0,0,0)))
    c=a.point_light_component;cb=seq.add_possessable(c);cb.set_parent(bind)
    ft=cb.add_track(unreal.MovieSceneFloatTrack);ft.set_property_name_and_path('Intensity','Intensity');s=ft.add_section();s.set_range(-48,337);ch=s.get_all_channels()[0]
    for time,value in [(-2,0),(1.4,0),(1.7,1800),(4.2,1800),(4.5,0),(4.65,0),(4.85,2700),(8.8,2700),(9.5,0),(14,0)]:ch.add_key(unreal.FrameNumber(round(time*24)),value,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
E.set_metadata_tag(seq,'Attribution',(R/'CREDITS.txt').read_text().strip());E.set_metadata_tag(seq,'Shot','12 seconds / 24 fps. One front-to-rear grid activation, full rear doors, 15% afterglow. World-space deterministic wake. Native Blueprint/Sequencer/materials.');E.save_loaded_asset(seq)
# A placed native player makes the shot runnable without editor Python.
player=A.spawn_actor_from_class(unreal.LevelSequenceActor,unreal.Vector());player.set_actor_label('SEQ_YU7_TunnelFlow');player.set_sequence(seq);player.set_folder_path('TunnelFlow')
settings=player.get_editor_property('playback_settings');settings.auto_play=False;player.set_editor_property('playback_settings',settings)
loc,rot=camera_at(0);camera.set_actor_location_and_rotation(unreal.Vector(*loc),unreal.Rotator(*rot),False,False)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key();level.set_level_viewport_camera_info(unreal.Vector(*loc),unreal.Rotator(*rot),key);level.set_level_viewport_fov(math.degrees(2*math.atan(36/80)),key);level.editor_set_viewport_realtime(True,key)
A.clear_actor_selection_set();assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'sequence':seq.get_path_name(),'frames':288,'fps':24,'speed_mps':15,'distance_m':180,'bindings':records,'mpc_key_tick_frames':[-48000,0,288000,336000],'camera':{str(t):camera_at(t) for t in [0,1,4,6.8,9.5,11.5,12]}}
(O/'sequence_v01.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
