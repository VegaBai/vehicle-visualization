import unreal,json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/lookdev')
D='/Game/YU7/Lookdev/Materials/'
M=unreal.MaterialEditingLibrary; E=unreal.EditorAssetLibrary
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
T=unreal.AssetToolsHelpers.get_asset_tools()
glass=unreal.load_asset(D+'M_YU7_ThinGlass')
# UE5.8 Substrate conversion uses root Opacity for an opaque layer above glass.
# SurfaceCoverage belongs on the ThinTranslucent output; keep that at one.
M.delete_all_material_expressions(glass)
def node(mat,typ,x,y,**p):
    n=M.create_material_expression(mat,getattr(unreal,typ),x,y); n.set_editor_properties(p); return n
def scalar(mat,name,val,y): return node(mat,'MaterialExpressionScalarParameter',-400,y,parameter_name=name,default_value=val)
def vec(mat,name,val,y): return node(mat,'MaterialExpressionVectorParameter',-800,y,parameter_name=name,default_value=unreal.LinearColor(*val,1))
def prop(n,p): assert M.connect_material_property(n,'',getattr(unreal.MaterialProperty,p))
def wire(a,o,b,p): assert M.connect_material_expressions(a,o,b,p)
trans=node(glass,'MaterialExpressionThinTranslucentMaterialOutput',0,0)
wire(vec(glass,'TransmissionTint',[.80,.87,.855],0),'RGB',trans,'TransmittanceColor')
wire(scalar(glass,'SurfaceCoverage',1.,100),'',trans,'SurfaceCoverage')
prop(scalar(glass,'OpaqueLayerAmount',0.,220),'MP_OPACITY')
prop(vec(glass,'OpaqueLayerColor',[0,0,0],320),'MP_BASE_COLOR')
prop(scalar(glass,'Roughness',.025,460),'MP_ROUGHNESS')
prop(scalar(glass,'Specular',.5,600),'MP_SPECULAR')
M.layout_material_expressions(glass); M.recompile_material(glass); E.save_loaded_asset(glass)
for name in ['MI_Glass_Clear','MI_Glass_Smoked','MI_Glass_Roof','MI_Glass_Lens']:
    mi=unreal.load_asset(D+name); M.clear_all_material_instance_parameters(mi)
    tint,rough={'MI_Glass_Clear':([.80,.87,.855],.025),'MI_Glass_Smoked':([.40,.48,.49],.03),'MI_Glass_Roof':([.18,.23,.25],.035),'MI_Glass_Lens':([.95,.97,.97],.018)}[name]
    M.set_material_instance_vector_parameter_value(mi,'TransmissionTint',unreal.LinearColor(*tint,1))
    M.set_material_instance_scalar_parameter_value(mi,'Roughness',rough)
    M.update_material_instance(mi); E.save_loaded_asset(mi)

path=D+'M_YU7_TrimMasked'
trim=unreal.load_asset(path) if E.does_asset_exist(path) else T.create_asset('M_YU7_TrimMasked',D[:-1],unreal.Material,unreal.MaterialFactoryNew())
M.delete_all_material_expressions(trim); trim.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
tex=node(trim,'MaterialExpressionTextureSampleParameter2D',-950,0,parameter_name='DetailTexture',texture=unreal.load_asset('/Game/Vehicles/YU7_Prepared/Textures/carPlastic_BrilliantBlackShape'))
color=vec(trim,'Tint',[.012,.015,.018],200)
mul=node(trim,'MaterialExpressionMultiply',-400,0); wire(tex,'RGB',mul,'A');wire(color,'RGB',mul,'B');prop(mul,'MP_BASE_COLOR')
assert M.connect_material_property(tex,'A',unreal.MaterialProperty.MP_OPACITY_MASK)
prop(scalar(trim,'Roughness',.23,300),'MP_ROUGHNESS'); prop(scalar(trim,'Metallic',0.,440),'MP_METALLIC');prop(scalar(trim,'Specular',.5,580),'MP_SPECULAR')
M.layout_material_expressions(trim); M.recompile_material(trim)
def inst(name,tint,rough,metal=0.,texture=None):
    mi=unreal.load_asset(D+name) if E.does_asset_exist(D+name) else T.create_asset(name,D[:-1],unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    M.set_material_instance_parent(mi,trim)
    M.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*tint,1))
    M.set_material_instance_scalar_parameter_value(mi,'Roughness',rough);M.set_material_instance_scalar_parameter_value(mi,'Metallic',metal)
    if texture: M.set_material_instance_texture_parameter_value(mi,'DetailTexture',unreal.load_asset(texture))
    M.update_material_instance(mi);E.save_loaded_asset(mi); return mi
black=inst('MI_Trim_Obsidian',[.012,.015,.018],.23)
silver=inst('MI_Trim_SatinMetal',[.42,.46,.49],.28,.95)
dark=inst('MI_Detail_Charcoal',[.025,.029,.033],.48,texture='/Game/Vehicles/YU7_Prepared/Textures/carHoodOutletPanelShape')
E.save_loaded_asset(trim)
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
changed=[]
for c in hero.get_components_by_class(unreal.StaticMeshComponent):
    for i,slot in enumerate(c.static_mesh.get_editor_property('static_materials')):
        name=slot.material_interface.get_name()
        new=black if name=='M_YU7_Plastic_SH' else dark if name=='M_YU7_dark_Gray_Map' else None
        if new: c.modify();c.set_material(i,new);changed.append({'component':c.get_name(),'slot':i,'new':new.get_name()})
rig=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_StudioLighting')
for c in rig.get_components_by_class(unreal.RectLightComponent):
    c.modify()
    if c.get_name()=='Key_Softbox':
        loc=unreal.Vector(-100,-100,480);rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(0,0,65))
        c.set_editor_properties({'relative_location':loc,'relative_rotation':rot,'source_width':640.,'source_height':170.,'intensity':44000.})
    elif c.get_name()=='Side_Strip': c.set_intensity(20000.)
    elif c.get_name()=='Roof_Ribbon': c.set_intensity(12000.)
    elif c.get_name()=='Front_Fill': c.set_intensity(12000.)
# A gentler clearcoat lobe still preserves a distinct sharp top layer.
for name in ['MI_Paint_MineralTeal','MI_Paint_Graphite']:
    mi=unreal.load_asset(D+name); M.set_material_instance_scalar_parameter_value(mi,'CoatRoughness',.11); M.update_material_instance(mi);E.save_loaded_asset(mi)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(OUT/'refine.json').write_text(json.dumps({'trim_assignments':changed,'glass_fix':'Root Opacity=0, ThinTranslucent SurfaceCoverage=1; separate TransmissionTint','key_softbox':[640,170,44000]},indent=2),encoding='utf-8')
RESULT={'trim_assignments':len(changed),'glass_root_opacity':0.,'thin_surface_coverage':1.}
