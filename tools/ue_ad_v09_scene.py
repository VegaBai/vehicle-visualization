"""Diagnosed lighting/environment revision, only v09 copies and map actors."""
import unreal,json,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(D+'/Maps/Studio_YU7_TunnelFlow_AD_v09')
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
assert 'YU7_AD_ShapingKey' not in actors
# Dim only copied tunnel emission graphs; preserve the historical environment.
for name in ['M_TunnelStrip','M_TunnelCyan']:
    mat=unreal.load_asset(D+'/Materials/'+name+'_AD_v09');mat.modify()
    old=M.get_material_property_input_node(mat,unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    factor=M.create_material_expression(mat,unreal.MaterialExpressionConstant);factor.r=.65
    mul=M.create_material_expression(mat,unreal.MaterialExpressionMultiply)
    assert M.connect_material_expressions(old,'',mul,'A');assert M.connect_material_expressions(factor,'',mul,'B')
    assert M.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    M.recompile_material(mat);E.save_loaded_asset(mat)
# Soft elongated road variation; paint/glass assets remain untouched.
road=unreal.load_asset(D+'/Materials/M_TunnelRoad_AD_v09');road.modify()
noise=M.create_material_expression(road,unreal.MaterialExpressionNoise);noise.set_editor_properties({'scale':1.,'quality':1,'levels':2,'output_min':0.,'output_max':1.})
pos=M.create_material_expression(road,unreal.MaterialExpressionWorldPosition)
scale=M.create_material_expression(road,unreal.MaterialExpressionConstant3Vector);scale.constant=unreal.LinearColor(.002,.025,.01,1)
mul=M.create_material_expression(road,unreal.MaterialExpressionMultiply);M.connect_material_expressions(pos,'',mul,'A');M.connect_material_expressions(scale,'',mul,'B');M.connect_material_expressions(mul,'',noise,'Position')
span=M.create_material_expression(road,unreal.MaterialExpressionMultiply);span.set_editor_property('const_b',.10);M.connect_material_expressions(noise,'',span,'A')
base=M.create_material_expression(road,unreal.MaterialExpressionAdd);base.set_editor_property('const_b',.34);M.connect_material_expressions(span,'',base,'A');M.connect_material_property(base,'',unreal.MaterialProperty.MP_ROUGHNESS)
M.recompile_material(road);E.save_loaded_asset(road)
bp=unreal.load_asset(D+'/Blueprints/BP_TunnelArchitecture_AD_v09');bp.modify()
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
record=[]
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    c=lib.get_object_for_blueprint(lib.get_data(h),bp)
    if isinstance(c,unreal.InstancedStaticMeshComponent):
        c.modify();name=c.get_name().replace('_GEN_VARIABLE','');kind=name.replace('Tunnel_','')
        if kind=='Lane':c.clear_instances();c.set_visibility(False);c.set_hidden_in_game(True)
        elif E.does_asset_exist(D+'/Materials/M_Tunnel'+kind+'_AD_v09'):c.set_material(0,unreal.load_asset(D+'/Materials/M_Tunnel'+kind+'_AD_v09'))
        if kind=='Strip':
            for i in range(c.get_instance_count()):
                tr=c.get_instance_transform(i,world_space=False)
                if abs(tr.translation.y)>900:tr.translation.z=335.;c.update_instance_transform(i,tr,world_space=False,mark_render_state_dirty=True,teleport=True)
        record.append({'name':name,'instances':c.get_instance_count()})
    if isinstance(c,unreal.RectLightComponent):
        c.modify();c.set_editor_properties({'intensity':29400.,'source_width':400.,'source_height':200.,'relative_rotation':unreal.Rotator(pitch=-90,yaw=0,roll=0),'temperature':6500.})
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);E.save_loaded_asset(bp)
old=actors['YU7_Tunnel_Architecture'];old.modify();old.set_actor_hidden_in_game(True);old.set_is_temporarily_hidden_in_editor(True);old.set_actor_label('YU7_Tunnel_Architecture_v08_Preserved')
arch=A.spawn_actor_from_class(E.load_blueprint_class(bp.get_path_name()),unreal.Vector());arch.set_actor_label('YU7_Tunnel_Architecture');arch.set_folder_path('TunnelFlow/Environment')
def update_rect(a,loc,target,intensity,width,height):
    a.modify();a.set_actor_location_and_rotation(unreal.Vector(*loc),unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target)),False,False)
    c=a.get_component_by_class(unreal.RectLightComponent);c.modify();c.set_editor_properties({'intensity':intensity,'source_width':width,'source_height':height})
    return c
update_rect(actors['YU7_Tunnel_FrontFill'],(-420,400,250),(-100,0,70),19600.,400.,180.)
update_rect(actors['YU7_Tunnel_SideFill'],(0,430,310),(0,0,95),12600.,400.,70.)
update_rect(actors['YU7_Tunnel_RoofFill'],(280,-180,420),(120,0,90),19500.,240.,100.)
def new_rect(label,loc,target,power,width,height,kelvin):
    a=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector(*loc));a.set_actor_label(label);a.set_folder_path('TunnelFlow/Lighting')
    c=update_rect(a,loc,target,power,width,height);c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_properties({'intensity_units':unreal.LightUnits.LUMENS,'attenuation_radius':1400.,'cast_shadows':True,'use_temperature':True,'temperature':kelvin,'specular_scale':1.})
    assert a.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False);return a
new_rect('YU7_AD_ShapingKey',(-200,220,300),(-170,0,100),11000.,200.,35.,6100.)
new_rect('YU7_AD_FarRim',(150,-240,280),(90,0,110),5000.,230.,25.,7200.)
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'diagnosed_front_glare':'RoofFill off removes windshield white block at frame 24','diagnosed_door_band':'SideFill off removes wide door reflection at frame 228','black_band_source':'YU7_Tunnel_Architecture.Tunnel_Lane, 2 instances, M_TunnelLane; NoLane native render removes both bands','environment_copy_instances':record,'fill_intensities_lumens':[19600,12600,19500],'strip_emission_factor':.65,'road_roughness':[.34,.44],'mineral_teal_material_modified':False,'visual_validation':'pending'}
(O/'scene_applied.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
