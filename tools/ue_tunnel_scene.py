"""Assemble native Blueprint environment and wheel pivots in the isolated map."""
import unreal,json,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()==D+'/Maps/Studio_YU7_TunnelFlow.Studio_YU7_TunnelFlow'
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero'];assert not E.does_asset_exist(D+'/Blueprints/BP_TunnelArchitecture')
# Hide preserved studio actors locally; keep the exact vehicle assembly.
for label,a in actors.items():
    keep=label=='YU7_Hero' or label.startswith('YU7_VP_') or label.startswith('YU7_BodyQuad_') or isinstance(a,unreal.PostProcessVolume)
    if keep:continue
    for c in a.get_components_by_class(unreal.SceneComponent):
        c.set_visibility(False,True);c.set_hidden_in_game(True,True)
    a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
    if isinstance(a,unreal.LevelSequenceActor):
        s=a.get_editor_property('playback_settings');s.auto_play=False;a.set_editor_property('playback_settings',s)
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
def bp_new(name):
    path=D+'/Blueprints/'+name;assert not E.does_asset_exist(path)
    bp=unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(path,unreal.Actor)
    h=next(h for h in sub.k2_gather_subobject_data_for_blueprint(bp) if isinstance(lib.get_object_for_blueprint(lib.get_data(h),bp),unreal.SceneComponent))
    return bp,h
def add(bp,parent,cls,name):
    h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent,new_class=cls,blueprint_context=bp));assert not str(reason),str(reason)
    assert sub.rename_subobject(h,name);return lib.get_object_for_blueprint(lib.get_data(h),bp)
def finish_bp(bp):
    assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);E.set_metadata_tag(bp,'Runtime','Native Blueprint components and Sequencer; no runtime Python');assert E.save_loaded_asset(bp)
def attach(a,parent):assert a.attach_to_actor(parent,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
def mesh_actor(name,mesh,material,attached=True):
    a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(name);a.set_folder_path('TunnelFlow/Effects')
    c=a.static_mesh_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(mesh);c.set_material(0,material);c.set_collision_profile_name('NoCollision');c.set_editor_properties({'cast_shadow':False,'receives_decals':False})
    if attached:a.set_actor_transform(hero.get_actor_transform(),False,False);attach(a,hero)
    return a
meshes=[unreal.load_asset(p) for p in E.list_assets(D+'/Meshes')];meshes=[m for m in meshes if isinstance(m,unreal.StaticMesh)]
for label in ['Body','Mirror_L','Mirror_R']:
    a=actors['YU7_BodyQuad_'+label];c=a.static_mesh_component
    mesh=next(m for m in meshes if 'TunnelGrid_'+label+'_' in m.get_name());c.set_static_mesh(mesh);c.set_material(0,unreal.load_asset(D+'/Materials/M_TunnelGrid'))
surface=mesh_actor('YU7_Tunnel_SurfaceFlow',next(m for m in meshes if 'SurfaceFlow' in m.get_name()),unreal.load_asset(D+'/Materials/M_TunnelSurfaceFlow'))
wake=mesh_actor('YU7_Tunnel_WorldWake',next(m for m in meshes if 'WorldWake' in m.get_name()),unreal.load_asset(D+'/Materials/M_TunnelWorldWake'),False)
# Four independent Blueprint wheel assemblies; six original meshes per wheel.
# Original component copies are hidden in this map only. Calipers stay fixed.
wheels=[];source=list(hero.get_components_by_class(unreal.StaticMeshComponent))
for label,ids,center in [('FL',range(90,96),(151.0407,83.53,38.2397)),('RL',range(96,102),(-148.2971,85.44,38.2397)),('RR',range(102,108),(-148.2971,-85.44,38.2397)),('FR',range(108,114),(151.0407,-83.53,38.2397))]:
    bp,h=bp_new('BP_TunnelWheel_'+label)
    root=lib.get_object_for_blueprint(lib.get_data(h),bp);root.set_mobility(unreal.ComponentMobility.MOVABLE)
    for i in ids:
        original=next(c for c in hero.get_components_by_class(unreal.StaticMeshComponent) if c.get_name().startswith('Part_%03d_'%i))
        c=add(bp,h,unreal.StaticMeshComponent,'Spin_'+str(i));c.set_static_mesh(original.static_mesh);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_collision_profile_name('NoCollision');c.set_editor_property('relative_location',unreal.Vector(*[-v for v in center]))
        for k in range(original.get_num_materials()):c.set_material(k,original.get_material(k))
        original.modify();original.set_visibility(False);original.set_hidden_in_game(True);original.set_editor_property('cast_shadow',False)
    finish_bp(bp)
    a=A.spawn_actor_from_class(E.load_blueprint_class(bp.get_path_name()),unreal.Vector(-center[0],-center[1],center[2]),unreal.Rotator(0,180,0));a.set_actor_label('YU7_Tunnel_Wheel_'+label);a.set_folder_path('TunnelFlow/Vehicle');attach(a,hero)
    wheels.append({'label':label,'actor':a.get_actor_label(),'local_center':center,'parts':list(ids)})

bp,h=bp_new('BP_TunnelArchitecture');root=lib.get_object_for_blueprint(lib.get_data(h),bp);root.set_mobility(unreal.ComponentMobility.STATIC)
cube=unreal.load_asset('/Engine/BasicShapes/Cube.Cube');components={};counts={}
for name in ['Wall','Ribs','Road','Strip','Cyan','Lane']:
    c=add(bp,h,unreal.InstancedStaticMeshComponent,'Tunnel_'+name);c.set_mobility(unreal.ComponentMobility.STATIC);c.set_static_mesh(cube);c.set_material(0,unreal.load_asset(D+'/Materials/M_Tunnel'+name));c.set_collision_profile_name('NoCollision');components[name]=c;counts[name]=0
def box(kind,loc,scale,roll=0):
    components[kind].add_instance(unreal.Transform(location=unreal.Vector(*loc),rotation=unreal.Rotator(0,0,roll),scale=unreal.Vector(*scale)),world_space=False);counts[kind]+=1
box('Road',(-10000,0,-8),(320,19,.15))
for sign in [-1,1]:
    box('Wall',(-10000,sign*960,175),(320,.2,3.5))
    box('Wall',(-10000,sign*835,475),(320,3.6,.2),sign*45)
    box('Ribs',(-10000,sign*925,25),(320,.35,.5))
    box('Cyan',(-10000,sign*903,52),(320,.025,.028))
    box('Lane',(-10000,sign*390,.05),(320,.09,.002))
box('Wall',(-10000,0,610),(320,14.5,.2))
for x in range(5500,-26001,-1000):
    for sign in [-1,1]:
        box('Ribs',(x,sign*937,175),(.18,.32,3.5));box('Ribs',(x,sign*817,474),(.18,3.55,.27),sign*45)
        box('Strip',(x-400,sign*650,590),(7.6,.07,.035))
        box('Strip',(x-400,sign*938,290),(7.6,.035,.07))
        for z in [110,210]:box('Ribs',(x-500,sign*945,z),(9.8,.025,.035))
    box('Ribs',(x,0,590),(.18,14,.27))
    # Broad, physically present overhead illumination reveals curved paint.
    c=add(bp,h,unreal.RectLightComponent,'CeilingLight_'+str(x).replace('-','N'));c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_properties({'relative_location':unreal.Vector(x-300,0,560),'relative_rotation':unreal.Rotator(-90,0,0),'intensity_units':unreal.LightUnits.LUMENS,'intensity':42000.,'source_width':650.,'source_height':450.,'attenuation_radius':1400.,'cast_shadows':False,'use_temperature':True,'temperature':7100.})
finish_bp(bp);arch=A.spawn_actor_from_class(E.load_blueprint_class(bp.get_path_name()),unreal.Vector());arch.set_actor_label('YU7_Tunnel_Architecture');arch.set_folder_path('TunnelFlow/Environment')

def rect(name,loc,target,intensity,width,height,color,shadow=False):
    a=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector(*loc));a.set_actor_label(name);a.set_folder_path('TunnelFlow/Lighting')
    a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target)),False)
    c=a.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_properties({'intensity_units':unreal.LightUnits.LUMENS,'intensity':intensity,'source_width':width,'source_height':height,'attenuation_radius':1800.,'cast_shadows':shadow,'specular_scale':.6})
    c.set_light_color(unreal.LinearColor(*color,1.),False);return a
lights=[]
for name,loc,target,intensity,w,ht,color in [('FrontFill',(-400,420,240),(-100,0,80),26000,500,240,(.64,.82,1.)),('SideFill',(0,480,250),(0,0,85),18000,700,160,(.42,.7,1.)),('RoofFill',(0,-140,520),(0,0,0),26000,500,300,(.75,.88,1.))]:
    a=rect('YU7_Tunnel_'+name,loc,target,intensity,w,ht,color);attach(a,hero);lights.append(a.get_actor_label())
for sign in [-1,1]:
    a=A.spawn_actor_from_class(unreal.PointLight,unreal.Vector(-200,sign*103,100));a.set_actor_label('YU7_Tunnel_ScanLight_'+('L' if sign==1 else 'R'));a.set_folder_path('TunnelFlow/Lighting')
    c=a.point_light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_properties({'intensity_units':unreal.LightUnits.LUMENS,'intensity':0.,'attenuation_radius':160.,'source_radius':12.,'cast_shadows':False});c.set_light_color(unreal.LinearColor(.25,.8,1,1),False)
    attach(a,hero)
post=next(a for a in actors.values() if isinstance(a,unreal.PostProcessVolume));s=post.settings
for k,v in {'auto_exposure_min_brightness':8.,'auto_exposure_max_brightness':8.,'auto_exposure_bias':.6,'bloom_intensity':.25,'bloom_threshold':1.,'vignette_intensity':.18,'motion_blur_amount':.3,'motion_blur_max':5.,'lumen_scene_lighting_quality':2.,'lumen_final_gather_quality':2.,'lumen_reflection_quality':2.}.items():s.set_editor_property(k,v);s.set_editor_property('override_'+k,True)
post.set_editor_property('settings',s);post.set_editor_property('unbound',True)
fog=A.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(0,0,-100));fog.set_actor_label('YU7_Tunnel_Haze');fog.set_folder_path('TunnelFlow/Environment')
f=fog.get_component_by_class(unreal.ExponentialHeightFogComponent);f.set_editor_properties({'fog_density':.006,'fog_height_falloff':.2,'start_distance':800.,'enable_volumetric_fog':True,'volumetric_fog_scattering_distribution':.4})
camera=A.spawn_actor_from_class(unreal.CineCameraActor,unreal.Vector(-720,510,110));camera.set_actor_label('CAM_YU7_TunnelFlow');camera.set_folder_path('TunnelFlow/Camera')
c=camera.get_cine_camera_component();film=c.filmback;film.sensor_width=36;film.sensor_height=20.25;c.filmback=film;c.set_editor_property('current_focal_length',40.);c.set_editor_property('current_aperture',8.)
focus=c.focus_settings;focus.focus_method=unreal.CameraFocusMethod.DISABLE;c.focus_settings=focus
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(0,0,77)),False)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'environment_blueprint':bp.get_path_name(),'environment_instances':counts,'wheels':wheels,'lights':lights,'world_wake_attached':wake.get_attach_parent_actor() is not None,'camera':camera.get_path_name(),'fixed_ev':8.}
(O/'scene_v01.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
