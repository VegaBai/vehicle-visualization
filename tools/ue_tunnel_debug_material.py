import unreal,json
from pathlib import Path
D='/Game/YU7/TunnelFlow';E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors={a.get_actor_label():a for a in A.get_all_level_actors()};rows=[]
for name,blend in [('M_Debug_ConstantAdditive',unreal.BlendMode.BLEND_ADDITIVE),('M_Debug_ConstantOpaque',unreal.BlendMode.BLEND_OPAQUE)]:
    assert not E.does_asset_exist(D+'/Materials/'+name);m=T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_properties({'shading_model':unreal.MaterialShadingModel.MSM_UNLIT,'blend_mode':blend,'two_sided':True})
    n=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-200,0);n.set_editor_property('constant',unreal.LinearColor(120,350,350,1));M.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    alpha=M.create_material_expression(m,unreal.MaterialExpressionConstant,-200,150);alpha.set_editor_property('r',1.);M.connect_material_property(alpha,'',unreal.MaterialProperty.MP_OPACITY)
    M.recompile_material(m);E.save_loaded_asset(m);rows.append({'name':name,'blend':str(m.get_editor_property('blend_mode')),'shading':str(m.get_editor_property('shading_model'))})
actors['YU7_BodyQuad_Body'].static_mesh_component.set_material(0,unreal.load_asset(D+'/Materials/M_Debug_ConstantOpaque'))
actors['YU7_Tunnel_SurfaceFlow'].static_mesh_component.set_material(0,unreal.load_asset(D+'/Materials/M_Debug_ConstantAdditive'))
for name,color,power,shadow in [('FrontFill',(.9,.97,1.),28000,True),('SideFill',(.85,1.,.97),18000,False),('RoofFill',(1.,.97,.9),30000,True)]:
    c=actors['YU7_Tunnel_'+name].get_component_by_class(unreal.RectLightComponent);c.set_light_color(unreal.LinearColor(*color,1),False);c.set_editor_properties({'intensity':power,'cast_shadows':shadow})
for label in ['L','R']:
    c=actors['YU7_Tunnel_ScanLight_'+label].point_light_component;c.set_editor_property('specular_scale',.05)
for name,color in [('M_TunnelWall',(.5,.65,.85)),('M_TunnelRibs',(.35,.5,.7)),('M_TunnelLane',(1.5,1.7,1.8))]:
    m=unreal.load_asset(D+'/Materials/'+name);n=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,800);n.set_editor_property('constant',unreal.LinearColor(*color,1));M.connect_material_property(n,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);M.recompile_material(m);E.save_loaded_asset(m)
unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0);unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'debug_materials':rows,'material_api':[n for n in dir(M) if 'expression' in n or 'property_input' in n]}
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/material_debug.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
