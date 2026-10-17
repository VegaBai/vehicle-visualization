import unreal,json
from pathlib import Path
m=unreal.load_asset('/Game/YU7/Lookdev/Materials/M_YU7_AutomotivePaint')
e=unreal.MaterialEditingLibrary
mi=unreal.load_asset('/Game/YU7/Lookdev/Materials/MI_Paint_PearlWhite')
RESULT={'master_scalars':list(map(str,e.get_scalar_parameter_names(m))),'mi_scalars':list(map(str,e.get_scalar_parameter_names(mi))),'vectors':list(map(str,e.get_vector_parameter_names(m))),'set_doc':e.set_material_instance_scalar_parameter_value.__doc__,'parent':str(mi.get_editor_property('parent')),'classes':[n for n in dir(unreal) if 'Material' in n and 'Library' in n]}
