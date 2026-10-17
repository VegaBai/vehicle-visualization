"""One-time isolated shot preparation. Refuses to overwrite an existing shot map."""
import unreal,json,hashlib
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/hero'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/Maps/Studio_YU7.Studio_YU7'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
SHOT='/Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero'
assert not E.does_asset_exist(SHOT),'Shot already exists; inspect and edit, do not recreate'
protected={}
for folder in ['art/FINAL_MODEL','VehicleStudio/Content/Vehicles/YU7_Prepared','VehicleStudio/Content/YU7/Lookdev','VehicleStudio/Content/YU7/Maps']:
    for p in (ROOT/folder).rglob('*'):
        if p.is_file():protected[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'VehicleStudio/Content/Studios/Levels/Studio_White.umap';protected[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'protected_before.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
assert unreal.EditorLoadingAndSavingUtils.save_map(world,SHOT)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).close_all_editors_for_asset(lvs)
reloaded=unreal.EditorLoadingAndSavingUtils.reload_packages([lvs.get_outermost()]);assert reloaded[0],str(reloaded)
world=unreal.EditorLoadingAndSavingUtils.load_map(SHOT);assert world
# The shot is deliberately fixed to teal. Do not carry bindings back to the lookdev map.
manager=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_VariantManager')
manager.set_level_variant_sets(None)
manager.set_actor_label('YU7_VariantManager_Unbound_ShotReference')
mapping={}
for old,new in [('MI_Paint_MineralTeal','MI_Hero_MineralTeal'),('MI_Glass_Clear','MI_Hero_GlassClear'),('MI_Studio_CoolGrey','MI_Hero_Studio')]:
    src='/Game/YU7/Lookdev/Materials/'+old;dest='/Game/YU7/Cinematics/Materials/'+new
    assert not E.does_asset_exist(dest)
    mi=E.duplicate_asset(src,dest);assert mi;mapping[src+'.'+old]=mi
assign=[]
for a in A.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        for i in range(c.get_num_materials()):
            old=c.get_material(i)
            if old and old.get_path_name() in mapping:
                c.modify();c.set_material(i,mapping[old.get_path_name()]);assign.append([a.get_actor_label(),c.get_name(),i])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'map':world.get_path_name(),'isolated_materials':[m.get_path_name() for m in mapping.values()],'assignments':len(assign),'variant_cache_reloaded':str(reloaded),'protected_files':len(protected)}
(OUT/'prepared.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
