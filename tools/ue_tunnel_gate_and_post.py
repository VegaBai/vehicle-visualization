import unreal,json
from pathlib import Path
D='/Game/YU7/TunnelFlow';E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
m=unreal.load_asset(D+'/Materials/M_TunnelGrid')
old=M.get_material_property_input_node(m,unreal.MaterialProperty.MP_OPACITY_MASK);assert old
time=M.create_material_expression(m,unreal.MaterialExpressionCollectionParameter,-1400,1500);time.set_editor_properties({'collection':unreal.load_asset(D+'/Materials/MPC_TunnelFlow'),'parameter_name':'ShotTime'})
gate=M.create_material_expression(m,unreal.MaterialExpressionSmoothStep,-1150,1500);gate.set_editor_properties({'const_min':5.02,'const_max':5.08});assert M.connect_material_expressions(time,'',gate,'Value')
mul=M.create_material_expression(m,unreal.MaterialExpressionMultiply,-900,1500);assert M.connect_material_expressions(old,'',mul,'A');assert M.connect_material_expressions(gate,'',mul,'B');assert M.connect_material_property(mul,'',unreal.MaterialProperty.MP_OPACITY_MASK)
M.layout_material_expressions(m);M.recompile_material(m);E.save_loaded_asset(m)
post=next(a for a in A.get_all_level_actors() if isinstance(a,unreal.PostProcessVolume));s=post.settings
names=['auto_exposure_method','auto_exposure_min_brightness','auto_exposure_max_brightness','auto_exposure_bias','bloom_method','bloom_intensity','bloom_threshold','translucency_type','motion_blur_amount']
before={n:str(s.get_editor_property(n)) for n in names}
for k,v in {'bloom_method':unreal.BloomMethod.BM_SOG,'bloom_intensity':.65,'bloom_threshold':.7}.items():s.set_editor_property(k,v);s.set_editor_property('override_'+k,True)
post.set_editor_property('settings',s)
matrows=[]
for name in ['M_TunnelGrid','M_TunnelRoad','M_TunnelWall','M_TunnelLane']:
    mat=unreal.load_asset(D+'/Materials/'+name)
    matrows.append({'name':name,'nodes':[e.get_class().get_name() for e in M.get_material_expressions(mat)],'emissive_node':str(M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_EMISSIVE_COLOR))})
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'reason':'Clamp made p=0 nose grid partially visible before 5 s; explicit sequence gate added to mask','post_before':before,'post_after':{n:str(s.get_editor_property(n)) for n in names},'materials':matrows}
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/gate_post_refine.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
