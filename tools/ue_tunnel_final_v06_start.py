import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports'
v=json.loads((O/'Previs_v06_1080p_validation.json').read_text());assert v['mp4_complete_decode'] and v['frames']==288
review=json.loads((O/'Previs_v06_1080p_frame_review.json').read_text());assert not review['abrupt_darkening_flags']
scope={'__name__':'__main__','AUDIT_NAME':'pre_final_v06_audit'};exec(compile((R/'tools/ue_tunnel_audit.py').read_text(),'ue_tunnel_audit.py','exec'),scope)
(O/'render_request.json').write_text(json.dumps({'name':'Final_v06_4K','width':3840,'height':2160,'spatial':1,'temporal':8}),encoding='utf-8')
exec(compile((R/'tools/ue_tunnel_render.py').read_text(),'ue_tunnel_render.py','exec'))
