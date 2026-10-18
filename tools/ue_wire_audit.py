"""Audit saved persistence before a final render without stopping the helper."""
import runpy
RESULT=runpy.run_path('C:/github2/vehicle_visualization/tools/ue_wire_finish.py',init_globals={'STOP_RUNNER':False,'RENDER_NAME':'Final_v03'})['RESULT']
