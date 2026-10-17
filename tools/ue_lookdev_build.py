"""Create editable lookdev assets; preserve all imported materials and geometry."""
import unreal, json, math
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization')
OUT=ROOT/'art/YU7_UNREAL/reports/lookdev'
DEST='/Game/YU7/Lookdev'
E=unreal.EditorAssetLibrary
M=unreal.MaterialEditingLibrary
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Maps/Studio_YU7.Studio_YU7'
backup='/Game/YU7/Maps/Studio_YU7_ImportBaseline'
if not E.does_asset_exist(backup):
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,backup)
tools=unreal.AssetToolsHelpers.get_asset_tools()
created=[]
def mat(name):
    path=DEST+'/Materials/'+name
    m=unreal.load_asset(path) if E.does_asset_exist(path) else tools.create_asset(name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    M.delete_all_material_expressions(m)
    created.append(m)
    return m
def node(m,typ,x,y,**props):
    n=M.create_material_expression(m,getattr(unreal,typ),x,y)
    n.set_editor_properties(props)
    return n
def scalar(m,name,value,x,y,group='Surface'):
    return node(m,'MaterialExpressionScalarParameter',x,y,parameter_name=name,default_value=value,group=group)
def vector(m,name,value,x,y,group='Surface'):
    return node(m,'MaterialExpressionVectorParameter',x,y,parameter_name=name,default_value=unreal.LinearColor(*value,1),group=group)
def wire(a,output,b,pin):
    assert M.connect_material_expressions(a,output,b,pin), (a.get_name(),pin)
def prop(n,p):
    assert M.connect_material_property(n,'',getattr(unreal.MaterialProperty,p))
def instance(name,parent,scalars={},vectors={}):
    path=DEST+'/Materials/'+name
    mi=unreal.load_asset(path) if E.does_asset_exist(path) else tools.create_asset(name,DEST+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    M.set_material_instance_parent(mi,parent)
    for k,v in scalars.items():
        M.set_material_instance_scalar_parameter_value(mi,k,v)
        assert abs(M.get_material_instance_scalar_parameter_value(mi,k)-v)<1e-5, k
    for k,v in vectors.items():
        M.set_material_instance_vector_parameter_value(mi,k,unreal.LinearColor(*v,1))
        actual=M.get_material_instance_vector_parameter_value(mi,k)
        assert max(abs(getattr(actual,a)-b) for a,b in zip(['r','g','b'],v))<1e-5, k
    M.update_material_instance(mi)
    created.append(mi)
    return mi

# Clean pigment + a separate clear-coat lobe. All colors are linear values.
paint=mat('M_YU7_AutomotivePaint')
paint.set_editor_properties({'use_material_attributes':True,'shading_model':unreal.MaterialShadingModel.MSM_CLEAR_COAT})
attrs=node(paint,'MaterialExpressionMakeMaterialAttributes',0,0)
prop(attrs,'MP_MATERIAL_ATTRIBUTES')
pins={str(p).lower().replace(' ','').replace('_',''):p for p in M.get_material_expression_input_names(attrs)}
base=vector(paint,'PigmentColor',[.04,.10,.12],-900,-180,'01 Pigment')
edge=vector(paint,'EdgeTint',[.08,.16,.17],-900,10,'01 Pigment')
fresnel=node(paint,'MaterialExpressionFresnel',-900,200,exponent=4.0,base_reflect_fraction=0.0)
flop=scalar(paint,'ColorFlop',.28,-900,370,'01 Pigment')
mul=node(paint,'MaterialExpressionMultiply',-640,230)
wire(fresnel,'',mul,'A'); wire(flop,'',mul,'B')
lerp=node(paint,'MaterialExpressionLinearInterpolate',-400,-50)
wire(base,'RGB',lerp,'A'); wire(edge,'RGB',lerp,'B'); wire(mul,'',lerp,'Alpha'); wire(lerp,'',attrs,pins['basecolor'])
for i,(name,value,pin) in enumerate([('Metallic',.65,'metallic'),('BaseRoughness',.25,'roughness'),('ClearCoat',1.,'clearcoat'),('CoatRoughness',.075,'clearcoatroughness'),('Specular',.5,'specular')]):
    n=scalar(paint,name,value,-380,180+i*130,'02 Finish'); wire(n,'',attrs,pins[pin])
M.layout_material_expressions(paint); M.recompile_material(paint)
pearl=instance('MI_Paint_PearlWhite',paint,{'Metallic':.15,'BaseRoughness':.27,'CoatRoughness':.085,'ColorFlop':.18},{'PigmentColor':[.64,.66,.65],'EdgeTint':[.80,.82,.80]})
teal=instance('MI_Paint_MineralTeal',paint,{'Metallic':.68,'BaseRoughness':.25,'CoatRoughness':.065,'ColorFlop':.32},{'PigmentColor':[.025,.095,.105],'EdgeTint':[.085,.19,.195]})
graphite=instance('MI_Paint_Graphite',paint,{'Metallic':.72,'BaseRoughness':.24,'CoatRoughness':.075,'ColorFlop':.25},{'PigmentColor':[.027,.032,.04],'EdgeTint':[.075,.09,.11]})

# Thin transmission keeps neutral highlights separate from glass absorption.
glass=mat('M_YU7_ThinGlass')
glass.set_editor_properties({'blend_mode':unreal.BlendMode.BLEND_TRANSLUCENT,'shading_model':unreal.MaterialShadingModel.MSM_THIN_TRANSLUCENT,'two_sided':True,'translucency_lighting_mode':unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING})
trans=node(glass,'MaterialExpressionThinTranslucentMaterialOutput',0,0)
transpins=list(M.get_material_expression_input_names(trans))
color=vector(glass,'TransmissionTint',[.78,.85,.84],-500,0,'01 Transmission')
wire(color,'RGB',trans,transpins[0])
black=node(glass,'MaterialExpressionConstant3Vector',-500,200,constant=unreal.LinearColor(0,0,0,1)); prop(black,'MP_BASE_COLOR')
for i,(name,value,pin) in enumerate([('Roughness',.025,'MP_ROUGHNESS'),('Specular',.5,'MP_SPECULAR'),('Coverage',1.,'MP_OPACITY')]):
    prop(scalar(glass,name,value,-500,350+i*140,'02 Surface'),pin)
M.layout_material_expressions(glass); M.recompile_material(glass)
clear=instance('MI_Glass_Clear',glass,{'Roughness':.025},{'TransmissionTint':[.80,.87,.855]})
smoke=instance('MI_Glass_Smoked',glass,{'Roughness':.03},{'TransmissionTint':[.40,.48,.49]})
roof=instance('MI_Glass_Roof',glass,{'Roughness':.035},{'TransmissionTint':[.18,.23,.25]})
lens=instance('MI_Glass_Lens',glass,{'Roughness':.018},{'TransmissionTint':[.95,.97,.97]})

studio=mat('M_StudioSurface')
prop(vector(studio,'Color',[.14,.16,.18],-400,0),'MP_BASE_COLOR')
prop(scalar(studio,'Roughness',.48,-400,200),'MP_ROUGHNESS')
prop(scalar(studio,'Specular',.32,-400,350),'MP_SPECULAR')
M.recompile_material(studio)
floor=instance('MI_Studio_CoolGrey',studio,{'Roughness':.47},{'Color':[.16,.18,.21]})

hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
assignments=[]
for c in hero.get_components_by_class(unreal.StaticMeshComponent):
    for i,slot in enumerate(c.static_mesh.get_editor_property('static_materials')):
        original=slot.material_interface.get_name()
        replacement=None
        if original.startswith('M_YU7_CarPaint'): replacement=teal
        elif original=='M_YU7_Windows': replacement=clear
        elif original=='M_YU7_D_Glass': replacement=roof
        elif original=='M_YU7_Light_Glass': replacement=lens
        if replacement:
            c.modify(); c.set_material(i,replacement)
            assignments.append({'component':c.get_name(),'slot':i,'original':original,'new':replacement.get_path_name()})
for a in A.get_all_level_actors():
    if a.get_actor_label().startswith('BP_CStand'):
        a.modify(); a.set_actor_hidden_in_game(True); a.set_folder_path('Reference/OriginalLighting_Hidden')
        for c in a.get_components_by_class(unreal.PrimitiveComponent):
            c.modify(); c.set_visibility(False); c.set_hidden_in_game(True); c.set_cast_shadow(False)
    if a.get_actor_label()=='RectLight':
        a.modify(); a.get_component_by_class(unreal.LightComponent).set_intensity(0)
        a.set_folder_path('Reference/OriginalLighting_Hidden')
    if a.get_actor_label() in ['SM_HalfDome','SM_InvertedCube']:
        c=a.get_component_by_class(unreal.StaticMeshComponent); c.modify()
        for i in range(c.get_num_materials()): c.set_material(i,floor)

# A native Blueprint lighting rig: no ticking script and no C++.
bp_path=DEST+'/Blueprints/BP_YU7_StudioLighting'
assert not E.does_asset_exist(bp_path), 'Lighting rig exists; adjust it instead of rebuilding'
bp=unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(bp_path,unreal.Actor)
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib=unreal.SubobjectDataBlueprintFunctionLibrary
hs=sub.k2_gather_subobject_data_for_blueprint(bp)
root=next(h for h in hs if isinstance(lib.get_object_for_blueprint(lib.get_data(h),bp),unreal.SceneComponent))
lights=[
    ('Key_Softbox',(-150,160,480),(0,0,55),600,260,60000,5600),
    ('Side_Strip',(60,390,240),(0,0,95),540,75,28000,6200),
    ('Rear_Rim',(270,-260,320),(60,0,90),440,85,48000,7000),
    ('Front_Fill',(-430,-160,230),(-130,0,70),240,230,16000,5200),
    ('Roof_Ribbon',(130,-40,520),(0,0,70),520,90,22000,6500),
    ('Backdrop_Wash',(360,-180,340),(600,-620,180),380,300,46000,6900),
]
for name,loc,target,w,h,power,temp in lights:
    handle,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.RectLightComponent,blueprint_context=bp))
    sub.rename_subobject(handle,name)
    c=lib.get_object_for_blueprint(lib.get_data(handle),bp)
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    rot=unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target))
    c.set_editor_properties({'relative_location':unreal.Vector(*loc),'relative_rotation':rot,'intensity_units':unreal.LightUnits.LUMENS,'intensity':power,'source_width':w,'source_height':h,'attenuation_radius':1800.,'use_temperature':True,'temperature':temp})
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
E.save_loaded_asset(bp)
rig=A.spawn_actor_from_class(E.load_blueprint_class(bp_path),unreal.Vector(0,0,0))
rig.set_actor_label('YU7_StudioLighting'); rig.set_folder_path('YU7/Lookdev')
post=next(a for a in A.get_all_level_actors() if isinstance(a,unreal.PostProcessVolume))
post.modify()
s=post.settings
settings={'auto_exposure_min_brightness':9.,'auto_exposure_max_brightness':9.,'auto_exposure_bias':1.0,'bloom_intensity':.12,'vignette_intensity':.12,'motion_blur_amount':0.,'lumen_scene_lighting_quality':4.,'lumen_final_gather_quality':4.,'lumen_reflection_quality':4.,'lumen_front_layer_translucency_reflections':True,'path_tracing_samples_per_pixel':256,'path_tracing_max_bounces':12}
for k,v in settings.items(): s.set_editor_property(k,v); s.set_editor_property('override_'+k,True)
post.set_editor_property('settings',s)
for m in created: E.save_loaded_asset(m)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
captures={'hero':list(unreal.VariantManagerLibrary.get_capturable_properties(hero)),'rig':list(unreal.VariantManagerLibrary.get_capturable_properties(rig))}
(OUT/'capturable.json').write_text(json.dumps(captures,indent=2),encoding='utf-8')
report={'baseline':backup,'assets':[x.get_path_name() for x in created]+[bp.get_path_name()],'assignments':assignments,'lights':lights,'postprocess':settings,'glass_input_pins':transpins}
(OUT/'build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
A.clear_actor_selection_set()
unreal.SystemLibrary.execute_console_command(world,'r.HighResScreenshotDelay 64')
RESULT={'assets':len(created)+1,'assignments':len(assignments),'lights':len(lights),'baseline':backup}
