"""Native Variant Manager asset, editor authored, runtime Blueprint callable."""
import unreal,json,itertools
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization'); OUT=ROOT/'art/YU7_UNREAL/reports/lookdev'
D='/Game/YU7/Lookdev'; E=unreal.EditorAssetLibrary; V=unreal.VariantManagerLibrary
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero')
rig=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_StudioLighting')
path=D+'/Variants/LVS_YU7_Lookdev'
assert not E.does_asset_exist(path),'Variant asset already exists; use targeted adjustments'
lvs=V.create_level_variant_sets_asset('LVS_YU7_Lookdev',D+'/Variants')
manager=V.create_level_variant_sets_actor(lvs);manager.set_actor_label('YU7_VariantManager');manager.set_folder_path('YU7/Lookdev')
capturable=list(V.get_capturable_properties(hero))
components={c.get_name():c for c in hero.get_components_by_class(unreal.StaticMeshComponent)}
groups={'Paint':[],'Glass':[],'WindowTrim':[]}
for c in components.values():
    for i,s in enumerate(c.static_mesh.get_editor_property('static_materials')):
        original=s.material_interface.get_name()
        group='Paint' if original.startswith('M_YU7_CarPaint') else 'Glass' if original=='M_YU7_Windows' else 'WindowTrim' if 'carWindowTrim' in c.get_name() else None
        if group:
            p=next(p for p in capturable if p.endswith(' / '+c.get_name()+' / Material['+str(i)+']'))
            groups[group].append({'component':c.get_name(),'slot':i,'property':p})
definitions={
    'Paint':{'Mineral Teal':'MI_Paint_MineralTeal','Pearl White':'MI_Paint_PearlWhite','Graphite':'MI_Paint_Graphite'},
    'Glass':{'Clear':'MI_Glass_Clear','Smoked':'MI_Glass_Smoked'},
    'WindowTrim':{'Obsidian':'MI_Trim_Obsidian','Satin Metal':'MI_Trim_SatinMetal'},
}
report={'asset':path,'groups':{},'bindings':groups,'combination_tests':[]}
sets={}
for group,choices in definitions.items():
    s=unreal.VariantSet();s.set_display_text(group);V.add_variant_set(lvs,s);sets[group]=s
    report['groups'][group]={}
    for name,mi_name in choices.items():
        v=unreal.Variant();v.set_display_text(name);V.add_variant(s,v);V.add_actor_binding(v,hero)
        mi=unreal.load_asset(D+'/Materials/'+mi_name)
        for binding in groups[group]:
            p=V.capture_property(v,hero,binding['property']); assert p,binding
            p.set_value_object(mi);assert p.has_recorded_data()
            assert p.get_value_object()==mi
        report['groups'][group][name]={'material':mi.get_path_name(),'captures':len(groups[group])}
lights={c.get_name():c for c in rig.get_components_by_class(unreal.RectLightComponent)}
lightpaths=list(V.get_capturable_properties(rig))
beauty={n:float(c.intensity) for n,c in lights.items()}
ratios={'Key_Softbox':.75,'Side_Strip':.5,'Rear_Rim':1.1,'Front_Fill':.4,'Roof_Ribbon':.5,'Backdrop_Wash':.6}
lighting={'Beauty':beauty,'Sculpted Contrast':{n:v*ratios[n] for n,v in beauty.items()}}
s=unreal.VariantSet();s.set_display_text('Lighting');V.add_variant_set(lvs,s);sets['Lighting']=s
report['groups']['Lighting']={}
for name,values in lighting.items():
    v=unreal.Variant();v.set_display_text(name);V.add_variant(s,v);V.add_actor_binding(v,rig)
    for n,value in values.items():
        path=next(p for p in lightpaths if p.endswith(' / '+n+' / Intensity'))
        p=V.capture_property(v,rig,path);assert p,path;p.set_value_float(value);assert p.has_recorded_data()
    report['groups']['Lighting'][name]={'intensities':values,'captures':len(values)}
# Exercise all independent combinations, checking actual component state after switching.
for paint,glass,trim,light in itertools.product(*[list(definitions[g]) for g in ['Paint','Glass','WindowTrim']],list(lighting)):
    choices={'Paint':paint,'Glass':glass,'WindowTrim':trim,'Lighting':light}
    for group,name in choices.items(): assert manager.switch_on_variant_by_name(group,name),(group,name)
    for group in definitions:
        expected=unreal.load_asset(D+'/Materials/'+definitions[group][choices[group]])
        current={c.get_name():c for c in hero.get_components_by_class(unreal.StaticMeshComponent)}
        for b in groups[group]: assert current[b['component']].get_material(b['slot'])==expected,(choices,b)
    for c in rig.get_components_by_class(unreal.RectLightComponent): assert abs(c.intensity-lighting[light][c.get_name()])<.01,(choices,c.get_name())
    report['combination_tests'].append({'choices':choices,'passed':True})
for group,name in {'Paint':'Mineral Teal','Glass':'Clear','WindowTrim':'Obsidian','Lighting':'Beauty'}.items(): assert manager.switch_on_variant_by_name(group,name)
credit=(ROOT/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
E.set_metadata_tag(lvs,'AssetCredit',credit)
E.set_metadata_tag(lvs,'BlueprintUsage','LevelVariantSetsActor > Switch on Variant by Name; group and variant strings as displayed. Bindings target YU7_Hero and YU7_StudioLighting in Studio_YU7.')
E.save_loaded_asset(lvs);unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(OUT/'variants.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
RESULT={'asset':lvs.get_path_name(),'groups':{g:list(v) for g,v in report['groups'].items()},'verified_combinations':len(report['combination_tests'])}
