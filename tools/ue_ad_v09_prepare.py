"""One-time isolated v09 map/sequence plus reversible lighting diagnostic copies."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09'
D='/Game/YU7/TunnelFlow/ArtDirection_v09';OLD='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert (O/'protected_before.json').exists()
assert not E.does_directory_exist(D)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
def load_map(path):
    lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
    unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
    assert unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()])[0]
    assert unreal.EditorLoadingAndSavingUtils.load_map(path)
def duplicate(src,dst):
    assert not E.does_asset_exist(dst);obj=E.duplicate_asset(src,dst);assert obj;assert E.save_loaded_asset(obj);return obj
mp=D+'/Maps/Studio_YU7_TunnelFlow_AD_v09';sp=D+'/Sequences/LS_YU7_TunnelFlow_AD_v09_12s'
duplicate(OLD+'/Maps/Studio_YU7_TunnelFlow',mp)
seq=duplicate(OLD+'/Sequences/LS_YU7_TunnelFlow_12s',sp)
load_map(mp)
def rebind(seq):
    actors={a.get_actor_label():a for a in A.get_all_level_actors()}
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
    unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).fix_actor_references()
    unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(0)
    resolved={}
    for b in seq.get_bindings():
        objs=unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(seq.get_binding_id(b))
        resolved[str(b.get_display_name())]=[o.get_path_name() for o in objs]
        assert objs,str(b.get_display_name())
    actors['SEQ_YU7_TunnelFlow'].set_sequence(seq)
    unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
    E.save_loaded_asset(seq);assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    return resolved
bound=rebind(seq)
copies={}
for category,names in [('Blueprints',['BP_TunnelArchitecture','BP_TunnelRoofAirflow_v01']),('Materials',['M_TunnelGrid','M_TunnelSurfaceFlow','M_TunnelWorldWake','M_TunnelRoofAirflow_Pulse_v02','M_TunnelRoad','M_TunnelWall','M_TunnelRibs','M_TunnelStrip','M_TunnelCyan'])]:
    for name in names:copies[OLD+'/'+category+'/'+name]=duplicate(OLD+'/'+category+'/'+name,D+'/'+category+'/'+name+'_AD_v09').get_path_name()
cases=['CleanBaseline','NoFront','NoSide','NoRoof','NoCeiling','NoRibs']
diagnostics=[]
for case in cases:
    dm=D+'/Diagnostics/Maps/Diag_'+case;ds=D+'/Diagnostics/Sequences/LS_Diag_'+case
    duplicate(mp,dm);sq=duplicate(sp,ds);load_map(dm);rebind(sq)
    actors={a.get_actor_label():a for a in A.get_all_level_actors()}
    for label,a in actors.items():
        if label.startswith('YU7_BodyQuad_') or label in ['YU7_Tunnel_SurfaceFlow','YU7_Tunnel_RoofAirflow','YU7_Tunnel_WorldWake']:
            for c in a.get_components_by_class(unreal.PrimitiveComponent):c.set_hidden_in_game(True)
        if label.startswith('YU7_Tunnel_ScanLight_'):a.point_light_component.set_visibility(False)
    for tag in ['Front','Side','Roof']:
        if case=='No'+tag:actors['YU7_Tunnel_'+tag+'Fill'].get_component_by_class(unreal.RectLightComponent).set_visibility(False)
    arch=actors['YU7_Tunnel_Architecture']
    for c in arch.get_components_by_class(unreal.SceneComponent):
        if case=='NoCeiling' and isinstance(c,unreal.RectLightComponent):c.set_visibility(False)
        if case=='NoRibs' and c.get_name()=='Tunnel_Ribs':c.set_hidden_in_game(True)
    assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    diagnostics.append({'case':case,'map':dm,'sequence':ds,'frames':[24,228]})
load_map(mp)
RESULT={'map':mp,'sequence':sp,'copies':copies,'bindings':bound,'diagnostics':diagnostics}
(O/'prepared.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
