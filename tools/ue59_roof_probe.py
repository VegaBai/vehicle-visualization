import unreal,json
from pathlib import Path
assert Path(unreal.Paths.project_dir()).resolve().name=='VehicleStudio_UE59'
w=unreal.EditorLevelLibrary.get_game_world();aa=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)
RESULT={a.get_actor_label():[{'name':c.get_name(),'visible':c.is_visible(),'hidden':c.get_editor_property('hidden_in_game'),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None} for c in a.get_components_by_class(unreal.StaticMeshComponent)] for a in aa if a.get_actor_label()=='YU7_Tunnel_RoofAirflow'}
