"""ONE-TIME isolated map, sequence and native collection-driven automotive finish."""
import unreal,json
exec(compile(open('C:/github2/vehicle_visualization/tools/yu7_finish_v11_common.py').read(),'finish_common','exec'))
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
assert not E.does_directory_exist(D)
assert (O/'protected_before.json').exists()
OLD='/Game/YU7/TunnelFlow/RoofSmooth_v10'
assert E.duplicate_asset(OLD+'/Maps/Studio_YU7_TunnelFlow_Smooth_v10',MAP)
seq=E.duplicate_asset(OLD+'/Sequences/LS_YU7_TunnelFlow_Smooth_v10_12s',SEQ);assert seq
assert E.save_loaded_asset(seq)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(MAP)
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
original=unreal.load_asset('/Game/YU7/Cinematics/Materials/MI_Hero_MineralTeal')
scalars=['Metallic','BaseRoughness','ClearCoat','CoatRoughness','Specular','ColorFlop','FlakeStrength']
vectors=['PigmentColor','EdgeTint']
for k in scalars:FINISHES[-1][k]=0. if k=='FlakeStrength' else M.get_material_instance_scalar_parameter_value(original,k)
for k in vectors:
    v=M.get_material_instance_vector_parameter_value(original,k);FINISHES[-1][k]=[v.r,v.g,v.b]
mpc=T.create_asset('MPC_YU7_Finish_v11',D+'/Materials',unreal.MaterialParameterCollection,unreal.MaterialParameterCollectionFactoryNew())
ss=[];vs=[]
for k in scalars:
    p=unreal.CollectionScalarParameter();p.set_editor_properties({'parameter_name':k,'default_value':FINISHES[0][k]});ss.append(p)
for k in vectors:
    p=unreal.CollectionVectorParameter();p.set_editor_properties({'parameter_name':k,'default_value':unreal.LinearColor(*FINISHES[0][k],1)});vs.append(p)
mpc.set_editor_properties({'scalar_parameters':ss,'vector_parameters':vs});assert E.save_loaded_asset(mpc)
paint=T.create_asset('M_YU7_Finish_v11',D+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
paint.set_editor_properties({'use_material_attributes':True,'shading_model':unreal.MaterialShadingModel.MSM_CLEAR_COAT})
def node(cls,**props):
    n=M.create_material_expression(paint,getattr(unreal,cls),0,0);n.set_editor_properties(props);return n
def link(a,b,pin,out=''):assert M.connect_material_expressions(a,out,b,pin),(a.get_name(),b.get_name(),pin)
def mul(a,b):
    n=node('MaterialExpressionMultiply');link(a,n,'A');link(b,n,'B');return n
def add(a,b):
    n=node('MaterialExpressionAdd');link(a,n,'A');link(b,n,'B');return n
def const(v):return node('MaterialExpressionConstant',r=v)
params={k:node('MaterialExpressionCollectionParameter',collection=mpc,parameter_name=k) for k in scalars+vectors}
attrs=node('MaterialExpressionMakeMaterialAttributes');assert M.connect_material_property(attrs,'',unreal.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
pins={str(p).lower().replace(' ','').replace('_',''):p for p in M.get_material_expression_input_names(attrs)}
fresnel=node('MaterialExpressionFresnel',exponent=4.,base_reflect_fraction=0.)
flop=mul(fresnel,params['ColorFlop'])
color=node('MaterialExpressionLinearInterpolate');link(params['PigmentColor'],color,'A');link(params['EdgeTint'],color,'B');link(flop,color,'Alpha')
# Microflakes use stable mesh UVs, so the pattern travels with the moving car.
uv=node('MaterialExpressionTextureCoordinate',u_tiling=1500.,v_tiling=1500.)
pos=node('MaterialExpressionAppendVector');link(uv,pos,'A');link(const(0),pos,'B')
noise=node('MaterialExpressionNoise',scale=1.,quality=1,levels=1,output_min=0.,output_max=1.)
link(pos,noise,'Position')
flake=mul(add(noise,const(-.5)),params['FlakeStrength'])
link(mul(color,add(const(1),flake)),attrs,pins['basecolor'])
link(add(params['BaseRoughness'],mul(flake,const(.16))),attrs,pins['roughness'])
for k,p in [('Metallic','metallic'),('ClearCoat','clearcoat'),('CoatRoughness','clearcoatroughness'),('Specular','specular')]:link(params[k],attrs,pins[p])
M.layout_material_expressions(paint);M.recompile_material(paint)
credits=(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
E.set_metadata_tag(paint,'Attribution',credits);assert E.save_loaded_asset(paint)
assigned=[]
for a in A.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if not c.is_visible() or c.get_editor_property('hidden_in_game'):continue
        for i in range(c.get_num_materials()):
            m=c.get_material(i)
            if m and m==original:
                c.modify();c.set_material(i,paint);assigned.append({'actor':a.get_actor_label(),'component':c.get_name(),'slot':i})
assert assigned
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).fix_actor_references()
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
for b in seq.get_bindings():
    objs=unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(seq.get_binding_id(b));assert objs,str(b.get_display_name());assert all(D+'/Maps/' in o.get_path_name() for o in objs)
actors['SEQ_YU7_TunnelFlow'].modify();actors['SEQ_YU7_TunnelFlow'].set_sequence(seq)
E.set_metadata_tag(seq,'Attribution',credits)
unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
assert E.save_loaded_asset(seq);assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(O/'palette.json').write_text(json.dumps(FINISHES,indent=2),encoding='utf-8')
RESULT={'map':MAP,'sequence':SEQ,'material':paint.get_path_name(),'collection':mpc.get_path_name(),'paint_assignments':assigned,'palette':FINISHES,'animation':'pending sequence authoring','visual_validation':'pending'}
(O/'prepared.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
