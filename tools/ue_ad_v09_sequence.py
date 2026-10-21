"""Bake continuous camera and native attached lighting; retain original drive/wheels."""
import unreal,json,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
exec(compile((R/'tools/yu7_ad_v09_motion.py').read_text(),'motion_authoring','exec'))
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(D+'/Maps/Studio_YU7_TunnelFlow_AD_v09')
seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_AD_v09_12s');seq.modify()
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
def transform(label,fn):
    b=next((b for b in seq.get_bindings() if str(b.get_display_name())==label),None)
    if b is None:b=seq.add_possessable(actors[label])
    tr=next((t for t in b.get_tracks() if isinstance(t,unreal.MovieScene3DTransformTrack)),None)
    if tr is None:tr=b.add_track(unreal.MovieScene3DTransformTrack)
    s=tr.get_sections()[0] if tr.get_sections() else tr.add_section();s.set_range(-48,337);s.set_editor_property('use_quaternion_interpolation',False)
    channels=s.get_all_channels()
    for c in channels:
        for key in c.get_keys():c.remove_key(key)
    for f in range(-48,337):
        loc,rot=fn(f/24)
        for c,v in zip(channels,[*loc,rot[2],rot[0],rot[1],1.,1.,1.]):c.add_key(unreal.FrameNumber(f),v,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    return b
transform('CAM_YU7_TunnelFlow',camera_at)
for tag,sign in [('L',-1),('R',1)]:
    transform('YU7_Tunnel_ScanLight_'+tag,lambda t,sign=sign:((250-500*(max(0.,min(1.,(t-1.5)/2.7)) if t<4.5 else body_head(t)),sign*106,105),(0,0,0)))
for b in seq.get_bindings():
    for tr in b.get_tracks():
        if isinstance(tr,unreal.MovieSceneFloatTrack) and str(tr.get_property_name())=='Intensity':
            ch=tr.get_sections()[0].get_all_channels()[0]
            for k in ch.get_keys():ch.remove_key(k)
            for f,v in [(-48,0),(36,0),(40,200),(98,200),(108,0),(114,380),(201,380),(216,120),(228,0),(336,0)]:ch.add_key(unreal.FrameNumber(f),v,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
def key_at(t):
    x=curve(t,[(0,300),(1.5,240),(4.5,65),(8.5,-100),(9.25,-165),(10,-160),(12,-135)])
    loc=unreal.Vector(x,-280,260);rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(x-70,0,85))
    return (loc.x,loc.y,loc.z),(rot.pitch,rot.yaw,rot.roll)
b=transform('YU7_AD_ShapingKey',key_at);component=actors['YU7_AD_ShapingKey'].get_component_by_class(unreal.RectLightComponent)
cb=seq.add_possessable(component);cb.set_parent(b);tr=cb.add_track(unreal.MovieSceneFloatTrack);tr.set_property_name_and_path('Intensity','Intensity');s=tr.add_section();s.set_range(-48,337);ch=s.get_all_channels()[0]
for f in range(-48,337):
    t=f/24;power=2300*(1+.25*smooth(8.75,9.15,t)*(1-smooth(9.3,9.75,t)))
    ch.add_key(unreal.FrameNumber(f),power,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
E.set_metadata_tag(seq,'Shot','v09: 114->204 head; 122->212 grid; 8-frame lag; primary lanes 5/6; 9.25 s climax; 11-12 s clean. Authored illustration, not CFD.')
assert E.save_loaded_asset(seq)
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq);unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).fix_actor_references();unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0);unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'fps':24,'frames':288,'native_camera_keys':385,'focal_length_mm':40,'angle_keys':ANGLE,'radius_keys':RADIUS,'height_keys':HEIGHT,'climax_key_light_factor':1.25,'original_drive_wheel_tracks_unchanged':True,'camera_safety_validation':'pending actual scene geometry sampling'}
(O/'sequence_applied.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
