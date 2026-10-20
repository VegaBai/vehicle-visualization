"""Read-only resume check before applying the prepared v08 material."""
import unreal
from pathlib import Path
E=unreal.EditorAssetLibrary
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
roof=next(a for a in actors if a.get_actor_label()=='YU7_Tunnel_RoofAirflow')
c=next(c for c in roof.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh)
RESULT={'world':world.get_path_name(),'rendering':unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering(),'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'roof_material':c.get_material(0).get_path_name(),'backup_exists':E.does_asset_exist('/Game/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow_BeforePulse_v07'),'new_material_exists':E.does_asset_exist('/Game/YU7/TunnelFlow/Materials/M_TunnelRoofAirflow_Pulse_v02')}
