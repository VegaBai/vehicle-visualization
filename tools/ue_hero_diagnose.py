"""Temporary per-light visual diagnostics; original intensities are restored."""
import unreal,time,json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/hero')
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lights={a.get_actor_label():a.get_component_by_class(unreal.RectLightComponent) for a in A.get_all_level_actors() if isinstance(a,unreal.RectLight) and a.get_actor_label().startswith('YU7_')}
powers={n:c.intensity for n,c in lights.items()}
camera=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='CAM_YU7_MineralHero')
loc=unreal.Vector(-780,880,235);rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(0,0,45))
camera.set_actor_location_and_rotation(loc,rot,False,True)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);level.set_level_viewport_camera_info(loc,rot,level.get_active_viewport_config_key())
stages=['Key_Softbox','Roof_Ribbon','Rear_Rim','Side_Strip']
state={'stage':-1,'next':time.monotonic(),'captured':False}
def tick(delta):
    now=time.monotonic()
    if now<state['next']:return
    if state['captured'] or state['stage']<0:
        for n,c in lights.items():c.set_intensity(powers[n])
        state['stage']+=1
        if state['stage']>=len(stages):
            unreal.unregister_slate_post_tick_callback(unreal._yu7_diag['handle'])
            (OUT/'diagnostics_done.json').write_text(json.dumps({'restored':True,'stages':stages}),encoding='utf-8')
            return
        lights['YU7_Light_'+stages[state['stage']]].set_intensity(0.)
        state['captured']=False;state['next']=now+3.
    else:
        unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(OUT/('without_'+stages[state['stage']]+'.png')),delay=0.)
        state['captured']=True;state['next']=now+8.
unreal._yu7_diag={'handle':unreal.register_slate_post_tick_callback(tick),'callback':tick,'lights':lights}
RESULT={'diagnostics_started':stages}
