import json
from pathlib import Path
import unreal
names = ['MaterialProperty','MaterialExpressionMakeMaterialAttributes','MaterialEditingLibrary','StaticMeshEditorSubsystem','StaticMesh','GeometryScript_MeshQueries','GeometryScript_ListUtils','GeometryScriptCopyMeshFromAssetOptions','GeometryScriptMeshReadLOD','GeometryScriptLODType','SubobjectDataBlueprintFunctionLibrary','UnrealEditorSubsystem','Actor','TextRenderComponent']
docs = {}
for name in names:
    cls = getattr(unreal, name, None)
    docs[name] = {'doc': str(getattr(cls, '__doc__', 'unavailable')), 'methods': {x: str(getattr(cls, x).__doc__) for x in dir(cls) if not x.startswith('_')}} if cls else None
Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/ue_probe_api.json').write_text(json.dumps(docs, indent=2), encoding='utf-8')
RESULT = {'material_properties': [x for x in dir(unreal.MaterialProperty) if x.startswith('MP_')], 'material_nodes': [x for x in dir(unreal) if 'MakeMaterialAttributes' in x], 'geometry_classes': [x for x in dir(unreal) if 'GeometryScript' in x and ('List' in x or 'Read' in x)]}
