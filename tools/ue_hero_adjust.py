"""Apply an explicitly saved shot configuration inside the isolated editor map."""
import unreal,json,math
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/hero'
r=json.loads((OUT/'adjust_request.json').read_text(encoding='utf-8-sig'))
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); E=unreal.EditorAssetLibrary; M=unreal.MaterialEditingLibrary
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero.Studio_YU7_MineralHero'
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
for name,p in r.get('lights',{}).items():
    a=actors.get(name)
    if not a:a=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector());a.set_actor_label(name);a.set_folder_path('YU7/HeroLights')
    a.modify();c=a.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE)
    if 'location' in p:
        loc=unreal.Vector(*p['location']);rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(*p['target']))
        a.set_actor_location_and_rotation(loc,rot,False,True)
    c.set_editor_properties({k:v for k,v in p.items() if k not in ['location','target']})
    c.set_editor_properties({'intensity_units':unreal.LightUnits.LUMENS,'attenuation_radius':2500.,'use_temperature':True,'source_texture':unreal.load_asset('/Game/YU7/Lookdev/Textures/T_SoftboxDiffuser')})
for name,p in r.get('materials',{}).items():
    mi=unreal.load_asset('/Game/YU7/Cinematics/Materials/'+name);assert mi
    for k,v in p.items():
        if isinstance(v,list):M.set_material_instance_vector_parameter_value(mi,k,unreal.LinearColor(*v,1))
        else:M.set_material_instance_scalar_parameter_value(mi,k,v)
    M.update_material_instance(mi);E.save_loaded_asset(mi)
post=next(a for a in actors.values() if isinstance(a,unreal.PostProcessVolume));s=post.settings
for k,v in r.get('post',{}).items():s.set_editor_property(k,v);s.set_editor_property('override_'+k,True)
post.set_editor_property('settings',s)
p=r.get('camera')
if p:
    a=actors.get('CAM_YU7_MineralHero')
    if not a:a=A.spawn_actor_from_class(unreal.CineCameraActor,unreal.Vector());a.set_actor_label('CAM_YU7_MineralHero');a.set_folder_path('YU7/Cinematics')
    loc=unreal.Vector(*p['location']);rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(*p['target']))
    a.set_actor_location_and_rotation(loc,rot,False,True);c=a.get_cine_camera_component()
    f=c.filmback;f.sensor_width=36.;f.sensor_height=20.25;c.set_editor_property('filmback',f)
    c.set_editor_properties({'current_focal_length':p['focal_length'],'current_aperture':8.})
    focus=c.focus_settings;focus.focus_method=unreal.CameraFocusMethod.DISABLE;c.set_editor_property('focus_settings',focus)
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);key=level.get_active_viewport_config_key()
    level.set_level_viewport_camera_info(loc,rot,key);level.set_level_viewport_fov(math.degrees(2*math.atan(36/(2*p['focal_length']))),key)
    level.editor_set_viewport_realtime(True,key)
A.clear_actor_selection_set();unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(OUT/(r['version']+'_settings.json')).write_text(json.dumps(r,indent=2),encoding='utf-8')
RESULT={'version':r['version'],'lights':len(r.get('lights',{})),'saved':True}
