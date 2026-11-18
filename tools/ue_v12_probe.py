"""Read-only authoring probe; source variant evaluation is not saved."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);E=unreal.EditorAssetLibrary
# Source variants dirty only the in-memory map; load_map discards these probe-only changes.
def load_map(path):
    for p in ['/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev','/Game/YU7/Itasha_v01/Variants/LVS_YU7_Itasha_v01']:
        a=unreal.load_asset(p);unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(a)
        assert unreal.EditorLoadingAndSavingUtils.reload_packages([a.get_outermost()])[0]
    assert unreal.EditorLoadingAndSavingUtils.load_map(path)
load_map('/Game/YU7/Itasha_v01/Maps/Studio_YU7_Itasha_v01')
actors={a.get_actor_label():a for a in A.get_all_level_actors()};manager=actors['YU7_ItashaOptions'];records={}
def vec(v):return [v.x,v.y,v.z]
for name in ['Rengoku','Zenitsu','Giyu']:
    assert manager.switch_on_variant_by_name('Itasha',name)
    rows=[]
    for label,a in actors.items():
        if not isinstance(a,unreal.DecalActor):continue
        c=a.get_component_by_class(unreal.DecalComponent);t=c.get_relative_transform();rot=t.rotation.rotator()
        rows.append(dict(label=label,location=vec(t.translation),rotation=[rot.pitch,rot.yaw,rot.roll],scale=vec(t.scale3d),size=vec(c.get_editor_property('decal_size')),material=c.get_decal_material().get_path_name(),sort_order=c.get_editor_property('sort_order')))
    assert len(rows)==5;records[name]=rows
assert manager.switch_on_variant_by_name('Itasha','Rengoku')
(O/'source_decals.json').write_text(json.dumps(records,indent=2))
load_map('/Game/YU7/TunnelFlow/FinishShowcase_v11/Maps/Studio_YU7_FinishShowcase_v11')
seq=unreal.load_asset('/Game/YU7/TunnelFlow/FinishShowcase_v11/Sequences/LS_YU7_FinishShowcase_v11_18s')
unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
bindings=[dict(name=str(b.get_display_name()),objects=[o.get_path_name() for o in unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(seq.get_binding_id(b))]) for b in seq.get_bindings()]
unreal.LevelSequenceEditorBlueprintLibrary.close_level_sequence()
RESULT={'bindings':bindings,'visibility_doc':unreal.MovieSceneVisibilityTrack.__doc__,'assign_doc':unreal.LevelSequenceEditorSubsystem.replace_binding_with_actors.__doc__ if hasattr(unreal.LevelSequenceEditorSubsystem,'replace_binding_with_actors') else str([x for x in dir(unreal.LevelSequenceEditorSubsystem) if 'actor' in x or 'binding' in x])}
(O/'probe.json').write_text(json.dumps(RESULT,indent=2))
