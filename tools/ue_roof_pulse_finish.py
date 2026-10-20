"""Finish v08 only after the native preview and selected 4K frames are validated."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports'
video=json.loads((O/'Previs_v08_1080p_validation.json').read_text())
assert video['frames']==288 and video['mp4_complete_decode'] and video['decoded_png_frames']
stills=json.loads((O/'Pulse_Keyframes_v08_4K_status.json').read_text())
assert stills['status']=='finished' and stills['success'] and not stills['errors']
scope={'__name__':'__main__'}
exec(compile((R/'tools/ue_roof_pulse_audit.py').read_text(),'ue_roof_pulse_audit.py','exec'),scope)
RESULT=scope['RESULT'];RESULT.update(video=video['video'],video_sha256=video['sha256'],still_resolution=[3840,2160],preview_resolution=[1920,1080],runner_shutdown_requested=True)
# Request normal runner shutdown on its next tick, after it writes this result.
(R/'art/YU7_UNREAL/reports/ue_jobs/request.json').write_text(json.dumps({'id':'pulse_session_closed','stop':True}),encoding='utf-8')
(O/'pulse_final_audit_v08.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
