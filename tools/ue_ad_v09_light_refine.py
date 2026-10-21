"""Refine overbright r05 native reflections without touching paint or exposure."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09';D='/Game/YU7/TunnelFlow/ArtDirection_v09'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev');unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0];assert unreal.EditorLoadingAndSavingUtils.load_map(D+'/Maps/Studio_YU7_TunnelFlow_AD_v09')
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
values={'YU7_AD_ShapingKey':(2300.,.6),'YU7_AD_FarRim':(1400.,.6),'YU7_Tunnel_RoofFill':(8000.,.35),'YU7_Tunnel_SideFill':(10000.,.45),'YU7_Tunnel_FrontFill':(18000.,.6)}
for label,(power,spec) in values.items():
    a=actors[label];a.modify();c=a.get_component_by_class(unreal.RectLightComponent);c.modify();c.set_editor_properties({'intensity':power,'specular_scale':spec})
a=actors['YU7_AD_ShapingKey'];loc=unreal.Vector(-300,280,260);target=unreal.Vector(-230,0,85);a.set_actor_location_and_rotation(loc,unreal.MathLibrary.find_look_at_rotation(loc,target),False,False)
bp=unreal.load_asset(D+'/Blueprints/BP_TunnelArchitecture_AD_v09');bp.modify();sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    c=lib.get_object_for_blueprint(lib.get_data(h),bp)
    if isinstance(c,unreal.RectLightComponent):c.modify();c.set_editor_properties({'intensity':6000.,'specular_scale':.2})
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);E.save_loaded_asset(bp)
for c in actors['YU7_Tunnel_Architecture'].get_components_by_class(unreal.RectLightComponent):c.modify();c.set_editor_properties({'intensity':6000.,'specular_scale':.2})
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'reason':'r05 first-frame roof/hood white areas too dominant; reduce light energy and shift key forward','lights':values,'ceiling_lumens':6000,'ceiling_specular_scale':.2,'paint_glass_exposure_unchanged':True}
(O/'lighting_r06.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
