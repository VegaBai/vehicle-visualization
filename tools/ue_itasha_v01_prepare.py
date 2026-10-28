"""ONE TIME: duplicate studio, import unmodified art and create native decal options."""
import unreal, json, math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_ITASHA/reports/v01'
D='/Game/YU7/Itasha_v01';MAP=D+'/Maps/Studio_YU7_Itasha_v01'
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();V=unreal.VariantManagerLibrary
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert not E.does_directory_exist(D),'One-time preparation: inspect partial state instead of rerunning'
assert (O/'protected_before.json').exists()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Maps/Studio_YU7.Studio_YU7'
assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)
old=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(old)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([old.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(MAP)
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
actors['YU7_VariantManager'].modify();actors['YU7_VariantManager'].set_level_variant_sets(None)
actors['YU7_VariantManager'].set_actor_label('YU7_OriginalVariantManager_Unbound')
actors['YU7_OriginalVariantManager_Unbound'] = actors.pop('YU7_VariantManager')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()

manifest=json.loads((R/'art/YU7_ITASHA/references/kimetsu_v01/sources.json').read_text(encoding='utf-8'))
chosen=[c for c in manifest['candidates'] if c['id'] in ['rengoku','zenitsu','giyu']]
textures={}
for row in chosen:
    task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(R/'art/YU7_ITASHA/references/kimetsu_v01'/row['file']),'destination_path':D+'/Textures','destination_name':'T_Itasha_'+row['id'],'automated':True,'replace_existing':False,'save':True})
    T.import_asset_tasks([task]);paths=task.get_editor_property('imported_object_paths');assert len(paths)==1,paths
    tex=unreal.load_asset(paths[0]);tex.set_editor_properties({'srgb':True,'address_x':unreal.TextureAddress.TA_CLAMP,'address_y':unreal.TextureAddress.TA_CLAMP,'compression_settings':unreal.TextureCompressionSettings.TC_EDITOR_ICON,'never_stream':True})
    E.set_metadata_tag(tex,'SourcePage',row['source_page']);E.set_metadata_tag(tex,'SourceImageSHA256',row['sha256'])
    E.set_metadata_tag(tex,'RightsStatus','Official reference artwork; reuse/redistribution license not verified. Local study.')
    assert E.save_loaded_asset(tex);textures[row['id']]=tex

mat=T.create_asset('M_Itasha_Artwork',D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
mat.set_editor_properties({'material_domain':unreal.MaterialDomain.MD_DEFERRED_DECAL,'blend_mode':unreal.BlendMode.BLEND_TRANSLUCENT})
def n(cls,**kw):
    o=M.create_material_expression(mat,getattr(unreal,cls),0,0);o.set_editor_properties(kw);return o
def link(a,b,pin,out=''):
    inputs=list(M.get_material_expression_input_names(b))
    actual=pin if pin in inputs else inputs[0] if len(inputs)==1 else pin
    assert M.connect_material_expressions(a,out,b,actual),(a,b,pin,inputs)
uv=n('MaterialExpressionTextureCoordinate')
scale=n('MaterialExpressionVectorParameter',parameter_name='UVScale',default_value=unreal.LinearColor(1,1,0,0))
sm=n('MaterialExpressionComponentMask',r=True,g=True);link(scale,sm,'Input')
off=n('MaterialExpressionVectorParameter',parameter_name='UVOffset',default_value=unreal.LinearColor(0,0,0,0))
om=n('MaterialExpressionComponentMask',r=True,g=True);link(off,om,'Input')
mul=n('MaterialExpressionMultiply');link(uv,mul,'A');link(sm,mul,'B')
add=n('MaterialExpressionAdd');link(mul,add,'A');link(om,add,'B')
sample=n('MaterialExpressionTextureSampleParameter2D',parameter_name='Artwork',texture=textures['rengoku']);link(add,sample,'UVs')
op=n('MaterialExpressionScalarParameter',parameter_name='PrintOpacity',default_value=1.)
alpha=n('MaterialExpressionMultiply');link(sample,alpha,'A','A');link(op,alpha,'B')
assert M.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
assert M.connect_material_property(alpha,'',unreal.MaterialProperty.MP_OPACITY)
M.layout_material_expressions(mat);M.recompile_material(mat);assert E.save_loaded_asset(mat)
instances={}
for name in ['None','Rengoku','Zenitsu','Giyu']:
    mi=T.create_asset('MI_Itasha_'+name,D+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    M.set_material_instance_parent(mi,mat)
    if name!='None':M.set_material_instance_texture_parameter_value(mi,'Artwork',textures[name.lower()])
    M.set_material_instance_scalar_parameter_value(mi,'PrintOpacity',0. if name=='None' else 1.)
    assert E.save_loaded_asset(mi);instances[name]=mi

# Restrict receivers inside the copied map. Original meshes/materials stay untouched.
receivers=[]
for a in A.get_all_level_actors():
    for c in a.get_components_by_class(unreal.PrimitiveComponent):
        ispaint=any(c.get_material(i) and c.get_material(i).get_name().startswith('MI_Paint_') for i in range(c.get_num_materials())) if isinstance(c,unreal.MeshComponent) else False
        c.modify();c.set_editor_property('receives_decals',ispaint)
        if ispaint and c.is_visible() and not c.get_editor_property('hidden_in_game'):receivers.append({'actor':a.get_actor_label(),'component':c.get_name()})
assert len(receivers)==9,receivers
decals=[]
# Uniform box per side; aspect correction is captured by each variant below.
for name,loc,rot in [('Left',(35,99,76),(0,-90,0)),('Right',(35,-99,76),(0,90,0)),('Hood',(-158,0,108),(-90,0,90))]:
    a=A.spawn_actor_from_class(unreal.DecalActor,unreal.Vector(*loc),unreal.Rotator(*rot))
    a.set_actor_label('YU7_Itasha_'+name);a.set_folder_path('YU7/Itasha')
    c=a.get_component_by_class(unreal.DecalComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_properties({'decal_size':unreal.Vector(25,90,43) if name!='Hood' else unreal.Vector(30,55,45),'fade_screen_size':0.,'sort_order':10})
    c.set_decal_material(instances['Rengoku'])
    assert a.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    decals.append(a)

lvs=V.create_level_variant_sets_asset('LVS_YU7_Itasha_v01',D+'/Variants')
manager=V.create_level_variant_sets_actor(lvs);manager.set_actor_label('YU7_ItashaOptions');manager.set_folder_path('YU7/Itasha')
options=unreal.VariantSet();options.set_display_text('Itasha');V.add_variant_set(lvs,options)
capture_report={}
for name in instances:
    v=unreal.Variant();v.set_display_text(name);V.add_variant(options,v)
    for a in decals:
        V.add_actor_binding(v,a);props=list(V.get_capturable_properties(a));capture_report[a.get_actor_label()]=props
        path=next(p for p in props if 'Decal Material' in p or p.endswith('Material[0]'))
        pv=V.capture_property(v,a,path);assert pv;pv.set_value_object(instances[name]);assert pv.has_recorded_data()
paintset=unreal.VariantSet();paintset.set_display_text('Paint');V.add_variant_set(lvs,paintset)
paint_choices={'Mineral Teal':'MI_Paint_MineralTeal','Pearl White':'MI_Paint_PearlWhite','Graphite':'MI_Paint_Graphite'}
for name,m in paint_choices.items():
    v=unreal.Variant();v.set_display_text(name);V.add_variant(paintset,v)
    for row in receivers:
        a=next(a for a in A.get_all_level_actors() if a.get_actor_label()==row['actor']);assert isinstance(a,unreal.StaticMeshActor)
        c=a.static_mesh_component;V.add_actor_binding(v,a)
        for i in range(c.get_num_materials()):
            if c.get_material(i).get_name().startswith('MI_Paint_'):
                prop=next(p for p in V.get_capturable_properties(a) if p.endswith(' / Material['+str(i)+']'))
                pv=V.capture_property(v,a,prop);assert pv;pv.set_value_object(unreal.load_asset('/Game/YU7/Lookdev/Materials/'+m))
assert manager.switch_on_variant_by_name('Itasha','Rengoku')
assert manager.switch_on_variant_by_name('Paint','Pearl White')
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
E.set_metadata_tag(lvs,'AssetCredit',credits)
E.set_metadata_tag(lvs,'BlueprintUsage','YU7_ItashaOptions: Switch on Variant by Name. Itasha: None/Rengoku/Zenitsu/Giyu. Paint: Mineral Teal/Pearl White/Graphite.')
E.set_metadata_tag(lvs,'ReloadRule','Save and reload this LVS package before reloading the map, or restart editor.')
E.save_loaded_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'map':MAP,'lvs':lvs.get_path_name(),'receivers':receivers,'decals':[a.get_actor_label() for a in decals],'capturable':capture_report,'status':'prepared; visual review and cross-frame switching pending'}
(O/'prepared.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
