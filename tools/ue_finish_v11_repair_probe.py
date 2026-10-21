import unreal,json
from pathlib import Path
p=Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/finish_v11')
m=unreal.load_asset('/Game/YU7/TunnelFlow/FinishShowcase_v11/Materials/M_YU7_Finish_v11')
# Expressions are editor data; get native class input names on transient probe material.
n=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionNoise,0,0)
RESULT={'noise_inputs':[str(x) for x in unreal.MaterialEditingLibrary.get_material_expression_input_names(n)],'key_get_time':unreal.MovieSceneScriptingFloatKey.get_time.__doc__,'color_key':unreal.MovieSceneParameterSection.add_color_parameter_key.__doc__,'get_scalar':unreal.MaterialEditingLibrary.get_scalar_parameter_value.__doc__ if hasattr(unreal.MaterialEditingLibrary,'get_scalar_parameter_value') else 'none','kismet_material':hasattr(unreal,'KismetMaterialLibrary')}
unreal.MaterialEditingLibrary.delete_material_expression(m,n)
(p/'repair_api.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
