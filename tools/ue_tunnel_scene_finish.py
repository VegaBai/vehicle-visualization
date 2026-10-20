import unreal,json,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors={a.get_actor_label():a for a in A.get_all_level_actors()}
assert 'CAM_YU7_TunnelFlow' not in actors
fog=actors['YU7_Tunnel_Haze'];wake=actors['YU7_Tunnel_WorldWake'];bp=unreal.load_asset(D+'/Blueprints/BP_TunnelArchitecture')
counts={c.get_name():c.get_instance_count() for c in actors['YU7_Tunnel_Architecture'].get_components_by_class(unreal.InstancedStaticMeshComponent)}
wheels=[{'label':label,'actor':'YU7_Tunnel_Wheel_'+label,'local_center':center,'parts':list(ids)} for label,ids,center in [('FL',range(90,96),(151.0407,83.53,38.2397)),('RL',range(96,102),(-148.2971,85.44,38.2397)),('RR',range(102,108),(-148.2971,-85.44,38.2397)),('FR',range(108,114),(151.0407,-83.53,38.2397))]]
lights=['YU7_Tunnel_'+s for s in ['FrontFill','SideFill','RoofFill']]
source=(R/'tools/ue_tunnel_scene.py').read_text();source=source[source.index('f=fog.get_component_by_class'):]
exec(compile(source,'ue_tunnel_scene_finish_body','exec'))
