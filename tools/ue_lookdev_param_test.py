import unreal
E=unreal.MaterialEditingLibrary
mi=unreal.load_asset('/Game/YU7/Lookdev/Materials/MI_Paint_PearlWhite')
r=E.set_material_instance_scalar_parameter_value(mi,'Metallic',.15)
RESULT={'return':r,'read':E.get_material_instance_scalar_parameter_value(mi,'Metallic'),'override':str(mi.get_editor_property('scalar_parameter_values'))}
