"""Avoid UE5.8 VariantManager stale SCS-component caches using native actor bindings.

Only switchable parts are exposed as attached native StaticMeshActors. Original
Blueprint meshes remain intact and their duplicate components are hidden in this map.
All runtime switching still uses native VariantManager / Blueprint nodes.
"""
import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/lookdev'
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);E=unreal.EditorAssetLibrary;V=unreal.VariantManagerLibrary
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
rig=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_StudioLighting')
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
old=json.loads((OUT/'variants.json').read_text(encoding='utf-8'))
groups=old['bindings']
expected_names=sorted({b['component'] for group in groups.values() for b in group})
assert not any(a.get_actor_label().startswith('YU7_VP_') for a in A.get_all_level_actors()),'Migration already started; inspect before resuming'
# Remove affected bindings without applying any old cached property.
for i in range(lvs.get_num_variant_sets()):
    s=lvs.get_variant_set(i)
    for j in range(s.get_num_variants()):
        v=s.get_variant(j)
        for a in [v.get_actor(k) for k in range(v.get_num_actors())]:V.remove_actor_binding(v,a)

parts={};record=[]
for name in expected_names:
    source=next(c for c in hero.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()==name)
    rel=source.relative_location;assert abs(rel.x)+abs(rel.y)+abs(rel.z)<.001
    actor=A.spawn_actor_from_class(unreal.StaticMeshActor,hero.get_actor_location(),hero.get_actor_rotation())
    actor.set_actor_label('YU7_VP_'+name.removeprefix('Part_'));actor.set_folder_path('YU7/VariantParts')
    c=actor.static_mesh_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_static_mesh(source.static_mesh)
    for i in range(source.get_num_materials()):c.set_material(i,source.get_material(i))
    c.set_collision_profile_name('NoCollision')
    assert actor.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    actor.set_editor_property('tags',['YU7VariantPart',name])
    # Editor property writes persist these overrides through reconstruction/reload.
    source.set_editor_properties({'visible':False,'hidden_in_game':True,'cast_shadow':False})
    parts[name]=actor;record.append({'source_component':name,'actor':actor.get_actor_label(),'mesh':c.static_mesh.get_path_name()})
native_lights={}
for source_name in ['Key_Softbox','Side_Strip','Rear_Rim','Front_Fill','Roof_Ribbon','Backdrop_Wash']:
    source=next(c for c in rig.get_components_by_class(unreal.RectLightComponent) if c.get_name()==source_name)
    p={k:source.get_editor_property(k) for k in ['intensity','intensity_units','source_width','source_height','attenuation_radius','use_temperature','temperature','source_texture','cast_shadows','specular_scale','indirect_lighting_intensity']}
    actor=A.spawn_actor_from_class(unreal.RectLight,source.relative_location,source.relative_rotation)
    actor.set_actor_label('YU7_Light_'+source_name);actor.set_folder_path('YU7/LookdevLights')
    c=actor.get_component_by_class(unreal.RectLightComponent);c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_properties(p)
    source.set_editor_properties({'intensity':0.,'visible':False,'hidden_in_game':True})
    native_lights[source_name]=actor
rig.set_folder_path('Reference/LightingBlueprint_Preserved')

definitions={'Paint':{'Mineral Teal':'MI_Paint_MineralTeal','Pearl White':'MI_Paint_PearlWhite','Graphite':'MI_Paint_Graphite'},'Glass':{'Clear':'MI_Glass_Clear','Smoked':'MI_Glass_Smoked'},'WindowTrim':{'Obsidian':'MI_Trim_Obsidian','Satin Metal':'MI_Trim_SatinMetal'}}
for group,choices in definitions.items():
    s=lvs.get_variant_set_by_name(group)
    for name,material in choices.items():
        v=s.get_variant_by_name(name)
        for b in groups[group]:
            actor=parts[b['component']];V.add_actor_binding(v,actor)
            path=next(p for p in V.get_capturable_properties(actor) if p.endswith(' / Material['+str(b['slot'])+']'))
            p=V.capture_property(v,actor,path);assert p;p.set_value_object(unreal.load_asset('/Game/YU7/Lookdev/Materials/'+material))
ratios={'Key_Softbox':.75,'Side_Strip':.5,'Rear_Rim':1.1,'Front_Fill':.4,'Roof_Ribbon':.5,'Backdrop_Wash':.6}
s=lvs.get_variant_set_by_name('Lighting')
for i in range(s.get_num_variants()):
    v=s.get_variant(i)
    for name,actor in native_lights.items():
        c=actor.get_component_by_class(unreal.RectLightComponent)
        power=c.intensity*(ratios[name] if str(v.get_display_text())=='Sculpted Contrast' else 1.)
        V.add_actor_binding(v,actor)
        path=next(p for p in V.get_capturable_properties(actor) if p.endswith(' / Intensity'))
        p=V.capture_property(v,actor,path);assert p;p.set_value_float(power)
E.set_metadata_tag(lvs,'BindingNotes','Native StaticMeshActor/RectLight bindings avoid UE5.8 stale Blueprint SCS component caches. Parts attach to YU7_Hero. Runtime API remains Blueprint Switch on Variant by Name.')
E.save_loaded_asset(lvs)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
RESULT={'native_variant_parts':len(parts),'native_lights':len(native_lights),'parts':record,'workaround':'native actor bindings, original Blueprint components preserved and hidden'}
(OUT/'stable_bindings.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
