"""Correct explicit Euler axes, preserve art aspect and add native colour sweep accents."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_ITASHA/reports/v01';D='/Game/YU7/Itasha_v01'
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();V=unreal.VariantManagerLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero'];manager=actors['YU7_ItashaOptions']
lvs=manager.get_level_variant_sets(True);options=lvs.get_variant_set_by_name('Itasha')
assert not E.does_asset_exist(D+'/Materials/M_Itasha_Sweep'),'One time sweep creation'
boxes={'Rengoku':(7,0,889,782),'Zenitsu':(245,0,750,566),'Giyu':(166,0,942,558)}
sizes={'Rengoku':(1000,782),'Zenitsu':(1000,566),'Giyu':(1000,558)}
for name in ['None','Rengoku','Zenitsu','Giyu']:
    ref='Rengoku' if name=='None' else name;x0,y0,x1,y1=boxes[ref];w,h=sizes[ref];ratio=(x1-x0)/(y1-y0)
    mi=unreal.load_asset(D+'/Materials/MI_Itasha_'+name)
    M.set_material_instance_vector_parameter_value(mi,'UVScale',unreal.LinearColor((x1-x0)/w,1,0,0));M.set_material_instance_vector_parameter_value(mi,'UVOffset',unreal.LinearColor(x0/w,0,0,0));assert E.save_loaded_asset(mi)
    v=options.get_variant_by_name(name)
    for side in ['Left','Right','Hood']:
        a=actors['YU7_Itasha_'+side];c=a.get_component_by_class(unreal.DecalComponent)
        if side=='Hood':
            a.set_actor_location_and_rotation(unreal.Vector(-157,0,108),unreal.Rotator(pitch=-90,yaw=0,roll=90),False,True)
            c.set_editor_property('decal_size',unreal.Vector(30,55,45));scale=unreal.Vector(1,1,110/ratio/90)
        else:
            a.set_actor_location_and_rotation(unreal.Vector(-22,99 if side=='Left' else -99,75),unreal.Rotator(pitch=0,yaw=-90 if side=='Left' else 90,roll=0),False,True)
            c.set_editor_property('decal_size',unreal.Vector(25,90,43));scale=unreal.Vector(1,84*ratio/180,84/86)
        c.set_editor_property('relative_scale3d',scale)
        pv=V.capture_property(v,a,'Decal Component / Relative Scale 3D');assert pv;pv.record()

mat=T.create_asset('M_Itasha_Sweep',D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());mat.set_editor_properties({'material_domain':unreal.MaterialDomain.MD_DEFERRED_DECAL,'blend_mode':unreal.BlendMode.BLEND_TRANSLUCENT})
def n(cls,**kw):
    o=M.create_material_expression(mat,getattr(unreal,cls),0,0);o.set_editor_properties(kw);return o
def link(a,b,pin,out=''):
    ps=list(M.get_material_expression_input_names(b));pin=pin if pin in ps else ps[0] if len(ps)==1 else pin
    assert M.connect_material_expressions(a,out,b,pin),(b,pin,ps)
def const(v):return n('MaterialExpressionConstant',r=v)
def op(cls,a,b=None):
    o=n('MaterialExpression'+cls);link(a,o,'A' if b is not None else 'Input')
    if b is not None:link(b,o,'B')
    return o
def mul(a,b):return op('Multiply',a,b)
def add(a,b):return op('Add',a,b)
def sub(a,b):return op('Subtract',a,b)
def sat(a):return op('Saturate',a)
def band(v,center,half):return sat(mul(sub(const(half),op('Abs',sub(v,center))),const(350)))
uv=n('MaterialExpressionTextureCoordinate');u=n('MaterialExpressionComponentMask',r=True,g=False,b=False,a=False);link(uv,u,'Input');vv=n('MaterialExpressionComponentMask',r=False,g=True,b=False,a=False);link(uv,vv,'Input')
# Long directional stripe with a thin secondary rail and diagonal interruption accents.
line=add(vv,mul(sub(u,const(.5)),const(.20)))
main=band(line,const(.57),.09);edge=band(line,const(.435),.012)
phase=op('Frac',mul(add(u,mul(vv,const(.13))),const(12)))
ticks=mul(band(line,const(.30),.05),sat(mul(sub(const(.20),phase),const(250))))
mask=sat(add(add(main,edge),ticks));ends=mul(sat(mul(u,const(12))),sat(mul(sub(const(1),u),const(12))))
enable=n('MaterialExpressionScalarParameter',parameter_name='PrintOpacity',default_value=1.)
alpha=mul(mul(mask,ends),enable)
col=n('MaterialExpressionVectorParameter',parameter_name='AccentColor',default_value=unreal.LinearColor(1,.16,.005,1))
color2=n('MaterialExpressionVectorParameter',parameter_name='SecondaryColor',default_value=unreal.LinearColor(1,.7,.02,1))
color=n('MaterialExpressionLinearInterpolate');link(col,color,'A');link(color2,color,'B');link(sat(add(edge,ticks)),color,'Alpha')
assert M.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR);assert M.connect_material_property(alpha,'',unreal.MaterialProperty.MP_OPACITY)
M.layout_material_expressions(mat);M.recompile_material(mat);assert E.save_loaded_asset(mat)
palette={'Rengoku':([.95,.06,.003],[1,.55,.015]),'Zenitsu':([1,.48,.005],[.005,.55,1]),'Giyu':([.005,.12,.7],[.18,.8,1]),'None':([0,0,0],[0,0,0])}
accent_mis={}
for name,(primary,secondary) in palette.items():
    mi=T.create_asset('MI_Itasha_Sweep_'+name,D+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew());M.set_material_instance_parent(mi,mat)
    for p,c in [('AccentColor',primary),('SecondaryColor',secondary)]:M.set_material_instance_vector_parameter_value(mi,p,unreal.LinearColor(*c,1))
    M.set_material_instance_scalar_parameter_value(mi,'PrintOpacity',0. if name=='None' else 1.);assert E.save_loaded_asset(mi);accent_mis[name]=mi
accent_actors=[]
for side,y,yaw in [('Left',99,-90),('Right',-99,90)]:
    a=A.spawn_actor_from_class(unreal.DecalActor,unreal.Vector(15,y,60),unreal.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label('YU7_Itasha_Sweep_'+side);a.set_folder_path('YU7/Itasha')
    c=a.get_component_by_class(unreal.DecalComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_properties({'decal_size':unreal.Vector(26,185,34),'fade_screen_size':0.,'sort_order':5});c.set_decal_material(accent_mis['Rengoku'])
    assert a.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    accent_actors.append(a)
    for name in palette:
        v=options.get_variant_by_name(name);V.add_actor_binding(v,a);pv=V.capture_property(v,a,'Decal Component / Decal Material');assert pv;pv.set_value_object(accent_mis[name])
assert manager.switch_on_variant_by_name('Itasha','Rengoku');assert manager.switch_on_variant_by_name('Paint','Pearl White')
assert E.save_loaded_asset(lvs);assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'layout':'v02','source_png_modified':False,'texture_transform':'alpha-bounds cropped in material UVs, source bytes preserved','art_bbox':boxes,'native_accent_actors':[a.get_actor_label() for a in accent_actors],'rotation_fix':'explicit keyword pitch/yaw/roll; positional Rotator args mapped unexpectedly'}
(O/'layout_v02.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
