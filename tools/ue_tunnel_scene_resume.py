"""Continue only unfinished wheel/architecture preparation after component reinstancing."""
import unreal,json,math
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero'];wake=actors['YU7_Tunnel_WorldWake']
source_code=(R/'tools/ue_tunnel_scene.py').read_text()
helpers=source_code[source_code.index('sub=unreal.get_engine_subsystem'):source_code.index('meshes=[unreal.load_asset')]
exec(compile(helpers,'scene_helpers','exec'))
original_new=bp_new;original_add=add
def bp_new(name):
    if name!='BP_TunnelWheel_FL':return original_new(name)
    bp=unreal.load_asset(D+'/Blueprints/'+name);assert bp
    h=next(h for h in sub.k2_gather_subobject_data_for_blueprint(bp) if isinstance(lib.get_object_for_blueprint(lib.get_data(h),bp),unreal.SceneComponent) and not isinstance(lib.get_object_for_blueprint(lib.get_data(h),bp),unreal.StaticMeshComponent))
    return bp,h
def add(bp,parent,cls,name):
    if bp.get_name()=='BP_TunnelWheel_FL' and name=='Spin_90':
        return next(lib.get_object_for_blueprint(lib.get_data(h),bp) for h in sub.k2_gather_subobject_data_for_blueprint(bp) if lib.get_object_for_blueprint(lib.get_data(h),bp).get_name()=='Spin_90_GEN_VARIABLE')
    return original_add(bp,parent,cls,name)
body=source_code[source_code.index('wheels=[];source='):]
exec(compile(body,'scene_resume_body','exec'))
