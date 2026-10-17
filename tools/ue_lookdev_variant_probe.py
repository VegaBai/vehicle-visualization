import unreal,json
V=unreal.VariantManagerLibrary
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
rig=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_StudioLighting')
s=lvs.get_variant_set_by_name('Lighting')
result={}
for i in range(s.get_num_variants()):
    v=s.get_variant(i)
    result[str(v.get_display_text())]={'stored':[{'path':p.get_full_display_string(),'type':p.get_property_type_string(),'value':p.get_value_float()} for p in V.get_captured_properties(v,rig)]}
    v.switch_on()
    result[str(v.get_display_text())]['actual']={c.get_name():c.intensity for c in rig.get_components_by_class(unreal.RectLightComponent)}
RESULT=result
