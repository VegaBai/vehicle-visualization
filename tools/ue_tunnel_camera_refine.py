import unreal,json,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow';E=unreal.EditorAssetLibrary
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
source=(R/'tools/ue_tunnel_sequence.py').read_text()
curve_code=source[source.index('def curve('):source.index('def transform(')]
camera_code=source[source.index('def camera_at('):source.index('camera_binding=transform')]
camera_code=camera_code.replace('(12,1060)','(12,930)')
exec(compile(curve_code+camera_code,'tunnel_camera_v06','exec'))
seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_12s')
b=next(b for b in seq.get_bindings() if str(b.get_display_name())=='CAM_YU7_TunnelFlow');track=next(t for t in b.get_tracks() if isinstance(t,unreal.MovieScene3DTransformTrack));channels=track.get_sections()[0].get_all_channels()
for c in channels:
    for key in c.get_keys():c.remove_key(key)
for f in range(-48,337,2):
    loc,rot=camera_at(f/24.)
    for c,v in zip(channels,[*loc,rot[2],rot[0],rot[1],1.,1.,1.]):c.add_key(unreal.FrameNumber(f),v,interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
ys=[camera_at(f/96)[0][1] for f in range(12*96+1)];assert max(ys)<910
E.save_loaded_asset(seq)
RESULT={'late_radius_cm':930,'max_camera_y_cm':max(ys),'wall_inner_y_cm':950,'minimum_clearance_cm':950-max(ys),'tested_subframe_samples':len(ys),'notes':'Changed only late camera radius; no vehicle/effect/material changes.'}
(O/'camera_v06.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
