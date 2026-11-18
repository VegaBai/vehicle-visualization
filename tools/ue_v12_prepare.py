"""One-time isolated film map and decal-safe vehicle; no runtime Python."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/itasha_v12'
D='/Game/YU7/TunnelFlow/ItashaShowcase_v12';MAP=D+'/Maps/Studio_YU7_ItashaShowcase_v12';SEQ=D+'/Sequences/LS_YU7_ItashaShowcase_v12_24s'
assert Path(unreal.Paths.project_dir()).resolve()==R/'VehicleStudio_UE59'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);L=unreal.LevelSequenceEditorBlueprintLibrary
assert not E.does_directory_exist(D),'One time only; inspect partial state on failure'
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/YU7/TunnelFlow/FinishShowcase_v11/Maps/')
assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)
seq=E.duplicate_asset('/Game/YU7/TunnelFlow/FinishShowcase_v11/Sequences/LS_YU7_FinishShowcase_v11_18s',SEQ);assert seq
actors={a.get_actor_label():a for a in A.get_all_level_actors()};old=actors['YU7_Hero']
bp=E.duplicate_asset('/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7',D+'/Blueprints/BP_YU7_ItashaFilm_v12');assert bp
source={c.get_name():c for c in old.get_components_by_class(unreal.StaticMeshComponent)}
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;seen=set()
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
    c=lib.get_object_for_blueprint(lib.get_data(h),bp)
    if not isinstance(c,unreal.StaticMeshComponent) or c.get_path_name() in seen:continue
    seen.add(c.get_path_name());src=source[c.get_name().removesuffix('_GEN_VARIABLE')]
    for i in range(src.get_num_materials()):c.set_material(i,src.get_material(i))
    c.set_editor_properties({'receives_decals':False,'visible':src.is_visible(),'hidden_in_game':src.get_editor_property('hidden_in_game'),'cast_shadow':src.get_editor_property('cast_shadow')})
    c.set_collision_profile_name('NoCollision')
assert len(seen)==121;assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert E.save_loaded_asset(bp)
hero=A.spawn_actor_from_class(E.load_blueprint_class(D+'/Blueprints/BP_YU7_ItashaFilm_v12'),old.get_actor_location(),old.get_actor_rotation());hero.set_actor_scale3d(old.get_actor_scale3d())
for a in old.get_attached_actors():assert a.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
L.open_level_sequence(seq);unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).fix_actor_references()
b=next(b for b in seq.get_bindings() if str(b.get_display_name())=='YU7_Hero')
unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem).replace_binding_with_actors([hero],b)
assert A.destroy_actor(old);hero.set_actor_label('YU7_Hero');hero.set_folder_path('YU7')
actors['SEQ_YU7_TunnelFlow'].modify();actors['SEQ_YU7_TunnelFlow'].set_sequence(seq)
receivers=[]
for a in A.get_all_level_actors():
    for c in a.get_components_by_class(unreal.PrimitiveComponent):
        paint=isinstance(c,unreal.StaticMeshComponent) and any(c.get_material(i) and c.get_material(i).get_name()=='M_YU7_Finish_v11' for i in range(c.get_num_materials()))
        c.modify();c.set_editor_property('receives_decals',paint)
        if paint:receivers.append(a.get_actor_label())
assert len(receivers)==9,receivers
records=json.loads((O/'source_decals.json').read_text());created=[]
for name,rows in records.items():
    for row in rows:
        a=A.spawn_actor_from_class(unreal.DecalActor,hero.get_actor_location(),hero.get_actor_rotation());a.set_actor_label(row['label']+'_'+name+'_v12');a.set_folder_path('YU7/ItashaFilm/'+name)
        assert a.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
        c=a.get_component_by_class(unreal.DecalComponent);p,y,r=row['rotation']
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_editor_properties({'relative_location':unreal.Vector(*row['location']),'relative_rotation':unreal.Rotator(pitch=p,yaw=y,roll=r),'relative_scale3d':unreal.Vector(*row['scale']),'decal_size':unreal.Vector(*row['size']),'fade_screen_size':0.,'sort_order':row['sort_order']})
        c.set_decal_material(unreal.load_asset(row['material']));a.set_actor_hidden_in_game(True)
        created.append(a.get_actor_label())
L.set_current_time(0);L.close_level_sequence()
E.set_metadata_tag(seq,'Attribution',(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip())
assert E.save_loaded_asset(seq);assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'map':MAP,'sequence':SEQ,'decals':created,'paint_receivers':receivers,'blueprint_templates':len(seen),'status':'assets prepared; timeline and visual verification pending'}
(O/'prepared.json').write_text(json.dumps(RESULT,indent=2))
