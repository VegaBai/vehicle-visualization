"""Saved-map native sequence validation prior to render."""
import unreal,json,hashlib
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12';D='/Game/YU7/TunnelFlow/ItashaShowcase_v12'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
E=unreal.EditorAssetLibrary;L=unreal.LevelSequenceEditorBlueprintLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
for p in ['/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev','/Game/YU7/Itasha_v01/Variants/LVS_YU7_Itasha_v01']:
    a=unreal.load_asset(p);unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(a);assert unreal.EditorLoadingAndSavingUtils.reload_packages([a.get_outermost()])[0]
assert unreal.EditorLoadingAndSavingUtils.load_map(D+'/Maps/Studio_YU7_ItashaShowcase_v12')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero']
seq=unreal.load_asset(D+'/Sequences/LS_YU7_ItashaShowcase_v12_24s');assert seq.get_playback_end()==576
L.open_level_sequence(seq)
bindings=[]
for b in seq.get_bindings():
    objs=L.get_bound_objects(seq.get_binding_id(b));assert objs,str(b.get_display_name());assert all(D+'/Maps/' in o.get_path_name() for o in objs)
    bindings.append({'name':str(b.get_display_name()),'objects':[o.get_path_name() for o in objs]})
decals=[a for a in actors.values() if isinstance(a,unreal.DecalActor)];assert len(decals)==15
assert all(a.get_attach_parent_actor()==hero for a in decals)
assert all(not c.get_editor_property('receives_decals') for c in hero.get_components_by_class(unreal.StaticMeshComponent))
assert all(not c.get_editor_property('receives_decals') for label,a in actors.items() if label.startswith('YU7_Tunnel_Wheel_') for c in a.get_components_by_class(unreal.StaticMeshComponent))
visible=[]
for label,a in actors.items():
    if a==hero or label.startswith('YU7_VP_') or label.startswith('YU7_Tunnel_Wheel_'):
        visible += [c.static_mesh.get_path_name() for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh and c.is_visible() and not c.get_editor_property('hidden_in_game')]
assert len(visible)==121 and len(set(visible))==121,(len(visible),len(set(visible)))
roof=[c for c in actors['YU7_Tunnel_RoofAirflow'].get_components_by_class(unreal.StaticMeshComponent) if c.is_visible() and not c.get_editor_property('hidden_in_game')];assert len(roof)==7
assert actors['YU7_Tunnel_WorldWake'].get_attach_parent_actor() is None
tri=sum(c.static_mesh.get_num_triangles(0) for label,a in actors.items() if label.startswith('YU7_BodyQuad_') for c in a.get_components_by_class(unreal.StaticMeshComponent));assert tri==99916
palette=json.loads((O/'sequence_applied.json').read_text())['palette'];mpc=unreal.load_asset('/Game/YU7/TunnelFlow/FinishShowcase_v11/Materials/MPC_YU7_Finish_v11');samples=[]
for f in [0,30,60,90,120,149,150,170,191,192,197,198,216,239,240,245,246,264,287,288,432,510,564,575]:
    L.set_current_time(f)
    shown=[a.get_actor_label() for a in decals if not a.get_editor_property('hidden')]
    expected='Rengoku' if 150<=f<192 else 'Zenitsu' if 198<=f<240 else 'Giyu' if 246<=f<288 else None
    assert len(shown)==(5 if expected else 0),(f,shown,expected)
    if expected:assert all(expected in n for n in shown)
    color=unreal.MaterialLibrary.get_vector_parameter_value(world,mpc,'PigmentColor')
    samples.append({'frame':f,'visible_decals':shown,'paint':[color.r,color.g,color.b],'hero_x':hero.get_actor_location().x})
for p in palette:
    L.set_current_time(p['frame']);c=unreal.MaterialLibrary.get_vector_parameter_value(world,mpc,'PigmentColor');assert max(abs(a-b) for a,b in zip([c.r,c.g,c.b],p['PigmentColor']))<1e-5
L.set_current_time(0);L.close_level_sequence()
protected=json.loads((O/'protected_before.json').read_text(encoding='utf-8-sig'));changed=[p['path'] for p in protected if hashlib.sha256((R/p['path']).read_bytes()).hexdigest()!=p['sha256']];assert not changed,changed
unreal.SystemLibrary.execute_console_command(world,'MAP CHECK')
RESULT={'status':'passed','frames':576,'bindings':bindings,'samples':samples,'unique_visible_meshes':121,'body_quad_triangles':tri,'visible_roof_lines':7,'protected_unchanged':len(protected),'native_runtime':'Blueprint/Sequencer/materials; editor Python validation only'}
(O/'scene_audit.json').write_text(json.dumps(RESULT,indent=2))
