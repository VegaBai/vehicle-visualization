"""Resume only the incomplete copied vehicle Blueprint after deduplicating handles."""
from pathlib import Path
R=Path('C:/github2/vehicle_visualization')
code=(R/'tools/ue_itasha_v01_receiver_fix.py').read_text(encoding='utf-8')
code=code.replace("assert not E.does_asset_exist(path)","assert E.does_asset_exist(path)")
code=code.replace("bp=E.duplicate_asset('/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7',path);assert bp","bp=unreal.load_asset(path);assert bp")
code=code.replace("RESULT={'copied_blueprint'","RESULT={'copied_blueprint'")
exec(compile(code,'itasha_receiver_resume','exec'))
