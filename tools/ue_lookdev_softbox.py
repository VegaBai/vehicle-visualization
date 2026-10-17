import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization'); D='/Game/YU7/Lookdev'
E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary
path=D+'/Textures/T_SoftboxDiffuser'
if not E.does_asset_exist(path):
    task=unreal.AssetImportTask();task.filename=str(ROOT/'art/YU7_UNREAL/Lookdev/T_SoftboxDiffuser.png');task.destination_path=D+'/Textures';task.automated=True;task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
tex=unreal.load_asset(path);tex.set_editor_property('srgb',False);E.save_loaded_asset(tex)
bp=unreal.load_asset(D+'/Blueprints/BP_YU7_StudioLighting')
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
powers={'Key_Softbox':44000.,'Side_Strip':20000.,'Rear_Rim':42000.,'Front_Fill':16000.,'Roof_Ribbon':10000.,'Backdrop_Wash':46000.}
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    c=lib.get_object_for_blueprint(lib.get_data(h),bp)
    if isinstance(c,unreal.RectLightComponent):
        name=c.get_name().removesuffix('_GEN_VARIABLE')
        p={'intensity':powers[name]}
        if name!='Backdrop_Wash':p['source_texture']=tex
        if name=='Key_Softbox':
            loc=unreal.Vector(-100,-100,480);rot=unreal.MathLibrary.find_look_at_rotation(loc,unreal.Vector(0,0,65))
            p.update({'relative_location':loc,'relative_rotation':rot,'source_width':640.,'source_height':170.})
        c.set_editor_properties(p)
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);E.save_loaded_asset(bp)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rig=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_StudioLighting')
# Apply via editor properties for persistent scene overrides, refreshing components each time.
for name in powers:
    c=next(c for c in rig.get_components_by_class(unreal.RectLightComponent) if c.get_name()==name)
    p={'intensity':powers[name]}
    if name!='Backdrop_Wash':p['source_texture']=tex
    if name=='Key_Softbox':p.update({'relative_location':unreal.Vector(-100,-100,480),'source_width':640.,'source_height':170.})
    c.set_editor_properties(p)
mi=unreal.load_asset(D+'/Materials/MI_Paint_MineralTeal')
for k,v in {'Metallic':.42,'BaseRoughness':.30,'CoatRoughness':.12,'ColorFlop':.18}.items():M.set_material_instance_scalar_parameter_value(mi,k,v)
M.set_material_instance_vector_parameter_value(mi,'EdgeTint',unreal.LinearColor(.045,.13,.14,1))
M.update_material_instance(mi);E.save_loaded_asset(mi)
# Update existing light variants; captures always resolve the current reconstructed components.
V=unreal.VariantManagerLibrary;lvs=unreal.load_asset(D+'/Variants/LVS_YU7_Lookdev')
s=lvs.get_variant_set_by_name('Lighting');ratios={'Key_Softbox':.75,'Side_Strip':.5,'Rear_Rim':1.1,'Front_Fill':.4,'Roof_Ribbon':.5,'Backdrop_Wash':.6}
for i in range(s.get_num_variants()):
    v=s.get_variant(i)
    for p in V.get_captured_properties(v,rig):
        n=p.get_full_display_string().split(' / ')[-2]
        p.set_value_float(powers[n]*(ratios[n] if str(v.get_display_text())=='Sculpted Contrast' else 1.))
for group,name in {'Paint':'Mineral Teal','Glass':'Clear','WindowTrim':'Obsidian','Lighting':'Beauty'}.items(): lvs.get_variant_set_by_name(group).get_variant_by_name(name).switch_on()
E.save_loaded_asset(lvs);unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'texture':tex.get_path_name(),'lights':{c.get_name():{'power':c.intensity,'source':str(c.source_texture)} for c in rig.get_components_by_class(unreal.RectLightComponent)}}
