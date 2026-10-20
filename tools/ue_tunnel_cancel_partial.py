import unreal,json
from pathlib import Path
state=unreal._yu7_tunnel_render
assert state['state']['request']['name']=='Final_v05_4K'
state['state']['review_stop_reason']='Full previs statistics identified camera clipping the tunnel wall at frames 269/287; revise late radius before final delivery.'
state['executor'].cancel_all_jobs()
RESULT={'cancel_requested':True,'preserve_partial_frames':True,'reason':state['state']['review_stop_reason']}
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/partial_render_stopped.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
