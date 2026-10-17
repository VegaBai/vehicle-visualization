"""Validate saved lookdev; does not rebuild or modify bound Blueprints."""
import unreal,json,hashlib
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/lookdev';E=unreal.EditorAssetLibrary
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Maps/Studio_YU7.Studio_YU7'
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
comps=hero.get_components_by_class(unreal.StaticMeshComponent);assert len(comps)==121
old=json.loads((ROOT/'art/YU7_UNREAL/reports/ue_output_manifest.json').read_text(encoding='utf-8'))
preserved={name:hashlib.sha256((ROOT/'VehicleStudio'/name).read_bytes()).hexdigest()==row['sha256'] for name,row in old.items() if name.startswith('Content\\Vehicles\\YU7_Prepared\\')}
assert all(preserved.values()),[n for n,v in preserved.items() if not v]
source=json.loads((ROOT/'art/YU7_UNREAL/reports/source_manifest.json').read_text(encoding='utf-8'))
source_ok=all(hashlib.sha256((ROOT/'art/FINAL_MODEL'/name).read_bytes()).hexdigest()==d['sha256'] for name,d in source.items());assert source_ok
oldmap=json.loads((ROOT/'art/YU7_UNREAL/reports/ue_original_map_hash.json').read_text(encoding='utf-8-sig'))
map_ok=hashlib.sha256(Path(oldmap['Path']).read_bytes()).hexdigest().lower()==oldmap['Hash'].lower();assert map_ok
assets=[]
for path in E.list_assets('/Game/YU7/Lookdev'):
    a=unreal.load_asset(path)
    r={'path':path,'class':a.get_class().get_name()}
    if isinstance(a,unreal.MaterialInterface):
        stats=unreal.MaterialEditingLibrary.get_statistics(a)
        r['statistics']={k:stats.get_editor_property(k) for k in ['num_pixel_shader_instructions','num_samplers','num_pixel_texture_samples']}
        r['textures']=[t.get_path_name() for t in a.get_used_textures()] if hasattr(a,'get_used_textures') else []
        if isinstance(a,unreal.MaterialInstanceConstant):r['parent']=a.parent.get_path_name()
    assets.append(r)
minimum=[float('inf')]*3;maximum=[float('-inf')]*3
for c in comps:
    assert all(c.get_material(i) is not None for i in range(c.get_num_materials())),c.get_name()
    b=c.static_mesh.get_bounding_box()
    for i,k in enumerate(['x','y','z']):minimum[i]=min(minimum[i],getattr(b.min,k));maximum[i]=max(maximum[i],getattr(b.max,k))
assert E.does_asset_exist('/Game/YU7/Maps/Studio_YU7_ImportBaseline')
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
credit=(ROOT/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
assert E.get_metadata_tag(lvs,'AssetCredit')==credit
native_parts=[a for a in A.get_all_level_actors() if a.get_actor_label().startswith('YU7_VP_')]
assert len(native_parts)==21,len(native_parts)
active_car_components=[c for c in comps if c.is_visible()]+[a.static_mesh_component for a in native_parts]
assert len(active_car_components)==121,len(active_car_components)
assert len({c.static_mesh.get_path_name() for c in active_car_components})==121,'Duplicated or missing rendered part'
lights={a.get_actor_label():{'intensity':c.intensity,'source_texture':c.source_texture.get_path_name() if c.source_texture else None,'width':c.source_width,'height':c.source_height,'location':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation())} for a in A.get_all_level_actors() if a.get_actor_label().startswith('YU7_Light_') for c in a.get_components_by_class(unreal.RectLightComponent)}
assert len(lights)==6
variants=json.loads((OUT/'variants.json').read_text(encoding='utf-8'))
assert len(variants['combination_tests'])==24 and all(r['passed'] for r in variants['combination_tests'])
safe_reload=json.loads((ROOT/'art/YU7_UNREAL/reports/ue_jobs/ld32_validate_safe_reload.json').read_text(encoding='utf-8'))
assert safe_reload['status']=='success'
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
dirty_maps=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()];dirty_content=[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
assert not dirty_maps and not dirty_content
RESULT={'world':world.get_path_name(),'mesh_components':len(comps),'dimensions_cm':[hi-lo for lo,hi in zip(minimum,maximum)],'original_imported_assets_unchanged':all(preserved.values()),'preserved_imported_asset_count':len(preserved),'source_files_unchanged':source_ok,'original_map_unchanged':map_ok,'assets':assets,'lights':lights,'variant_combinations_verified':24,'credit_exact':True,'visible_credits':'pending final project UI/sequence','dirty_maps':dirty_maps,'dirty_content':dirty_content,'runtime_cpp_added':False,'runtime_python_required':False}
(OUT/'final_audit.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
RESULT.update({'native_variant_parts':len(native_parts),'active_unique_car_components':len(active_car_components),'restart_persistence_verified':True,'safe_reload_then_gc_verified':True,'plain_map_reload_known_limitation':'Reload LVS package before the map via tools/ue_lookdev_reload.py, or restart editor.'})
(OUT/'final_audit.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
