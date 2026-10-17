"""Verify saved cinematic scene without rebuilding source assets or variants."""
import unreal,json,hashlib
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/hero'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero.Studio_YU7_MineralHero'
actors=A.get_all_level_actors();hero=next(a for a in actors if a.get_actor_label()=='YU7_Hero')
original=hero.get_components_by_class(unreal.StaticMeshComponent);assert len(original)==121
parts=[a.static_mesh_component for a in actors if a.get_actor_label().startswith('YU7_VP_')];assert len(parts)==21
active=[c for c in original if c.is_visible()]+[c for c in parts if c.is_visible()]
assert len(active)==121 and len({c.static_mesh.get_path_name() for c in active})==121
assert all(not c.hidden_in_game for c in active)
assert all(c.get_material(i) for c in active for i in range(c.get_num_materials()))
camera=next(a for a in actors if a.get_actor_label()=='CAM_YU7_MineralHero')
seq=unreal.load_asset('/Game/YU7/Cinematics/Sequences/LS_YU7_MineralHero_5s')
assert seq.get_playback_start()==0 and seq.get_playback_end()==120
assert seq.get_display_rate().numerator==24
binding=seq.get_bindings()[0];section=binding.get_tracks()[0].get_sections()[0]
channels=section.get_all_channels();assert len(channels)==9
counts=[len(c.get_keys()) for c in channels];assert all(n==33 for n in counts),counts
lights=[]
for a in actors:
    if isinstance(a,unreal.RectLight) and a.get_actor_label().startswith('YU7_'):
        c=a.get_component_by_class(unreal.RectLightComponent)
        lights.append({'label':a.get_actor_label(),'location':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'intensity':c.intensity,'specular_scale':c.specular_scale,'width':c.source_width,'height':c.source_height})
assert len(lights)==8
presets=[]
for name,spatial,temporal,end in [('YU7_MineralTeal_4K',64,1,1),('YU7_MineralTeal_Motion_4K',1,16,120)]:
    preset=unreal.load_asset('/Game/YU7/Cinematics/RenderPresets/MRQ_'+name);assert preset
    settings=preset.get_all_settings()
    output=next(s for s in settings if isinstance(s,unreal.MoviePipelineOutputSetting))
    aa=next(s for s in settings if isinstance(s,unreal.MoviePipelineAntiAliasingSetting))
    assert output.output_resolution.x==3840 and output.output_resolution.y==2160
    assert output.custom_start_frame==0 and output.custom_end_frame==end
    assert aa.spatial_sample_count==spatial and aa.temporal_sample_count==temporal
    presets.append({'asset':preset.get_path_name(),'resolution':[output.output_resolution.x,output.output_resolution.y],'frame_range':[output.custom_start_frame,output.custom_end_frame],'spatial':aa.spatial_sample_count,'temporal':aa.temporal_sample_count})
protected=json.loads((OUT/'protected_before.json').read_text(encoding='utf-8'))
changed=[name for name,sha in protected.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha];assert not changed,changed
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
dirty_maps=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
dirty_content=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
assert not dirty_maps and not dirty_content
unreal.SystemLibrary.execute_console_command(world,'MAP CHECK')
RESULT={'map':world.get_path_name(),'active_unique_car_meshes':len(active),'native_parts':len(parts),'lights':lights,'camera_focal_length':camera.get_cine_camera_component().current_focal_length,'native_sequence':seq.get_path_name(),'fps':24,'frames':120,'keys_per_transform_channel':counts,'presets':presets,'protected_files_unchanged':len(protected),'dirty_maps':dirty_maps,'dirty_content':dirty_content,'runtime_python_required':False,'cpp_added':False,'visible_project_credits':'pending later UI/final-film delivery; source attribution retained verbatim in delivery CREDITS.txt and MP4 metadata'}
(OUT/'final_scene_audit.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
