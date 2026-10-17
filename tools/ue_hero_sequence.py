"""Native camera animation: 120 frames at 24 fps, with pre-roll handles."""
import unreal,json,math
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/hero')
T=unreal.AssetToolsHelpers.get_asset_tools();E=unreal.EditorAssetLibrary
DEST='/Game/YU7/Cinematics/Sequences';path=DEST+'/LS_YU7_MineralHero_5s'
assert not E.does_asset_exist(path),'Sequence exists; adjust existing tracks deliberately'
camera=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='CAM_YU7_MineralHero')
seq=T.create_asset('LS_YU7_MineralHero_5s',DEST,unreal.LevelSequence,unreal.LevelSequenceFactoryNew());assert seq
seq.set_display_rate(unreal.FrameRate(24,1));seq.set_tick_resolution_directly(unreal.FrameRate(24000,1))
seq.set_playback_start(0);seq.set_playback_end(120)
seq.set_work_range_start(-2.);seq.set_work_range_end(6.);seq.set_view_range_start(-0.2);seq.set_view_range_end(5.2)
bind=seq.add_possessable(camera)
track=bind.add_track(unreal.MovieScene3DTransformTrack);section=track.add_section();section.set_range(-48,145)
channels=section.get_all_channels();assert len(channels)==9,len(channels)
# Gentle 8-degree dolly arc, analytic eased motion sampled into native keys.
keys=[]
for f in [-48]+list(range(0,121,4))+[144]:
    t=max(0.,min(1.,f/120.));u=t*t*(3-2*t)
    angle=math.radians(131.55-7.5*u);radius=1176-30*u
    loc=unreal.Vector(radius*math.cos(angle),radius*math.sin(angle),235-8*u)
    target=unreal.Vector(0,0,45)
    rot=unreal.MathLibrary.find_look_at_rotation(loc,target)
    values=[loc.x,loc.y,loc.z,rot.roll,rot.pitch,rot.yaw,1.,1.,1.]
    for c,v in zip(channels,values):c.add_key(unreal.FrameNumber(f),v,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    keys.append({'frame':f,'location':[loc.x,loc.y,loc.z],'rotation':[rot.pitch,rot.yaw,rot.roll]})
cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(-48,145)
cut.set_camera_binding_id(seq.get_binding_id(bind))
E.set_metadata_tag(seq,'ShotNotes','Mineral teal 5 second camera arc. 24 fps, frames 0-119. Native Sequencer keys, no runtime Python.');E.save_loaded_asset(seq)
RESULT={'sequence':seq.get_path_name(),'fps':24,'frames':120,'duration_seconds':5,'keys':keys,'channels':[str(c.channel_name) for c in channels]}
(OUT/'sequence.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
