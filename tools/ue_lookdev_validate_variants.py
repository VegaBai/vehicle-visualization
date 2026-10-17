import unreal,json,itertools,re
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL/reports/lookdev'
E=unreal.EditorAssetLibrary;V=unreal.VariantManagerLibrary
unreal.collect_garbage()
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lvs=unreal.load_asset('/Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev')
manager=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_VariantManager')
sets={str(s.get_display_text()):s for s in [lvs.get_variant_set(i) for i in range(lvs.get_num_variant_sets())]}
choices={g:[str(s.get_variant(i).get_display_text()) for i in range(s.get_num_variants())] for g,s in sets.items()}
report={'asset':lvs.get_path_name(),'groups':{},'combination_tests':[]}
def check_variant(v):
    rows=[]
    for i in range(v.get_num_actors()):
        a=v.get_actor(i);assert a,'Unresolved actor binding'
        comps={c.get_name():c for c in a.get_components_by_class(unreal.ActorComponent)}
        for p in V.get_captured_properties(v,a):
            path=p.get_full_display_string();parts=path.split(' / ')
            assert p.has_recorded_data(),path
            if 'Material[' in parts[-1]:
                c=a.get_component_by_class(unreal.StaticMeshComponent)
                slot=int(re.search(r'Material\[(\d+)\]',parts[-1]).group(1))
                expected=p.get_value_object();actual=c.get_material(slot);assert actual==expected,(path,str(actual),str(expected))
                value=expected.get_path_name()
            elif parts[-1]=='Intensity':
                c=a.get_component_by_class(unreal.RectLightComponent)
                expected=p.get_value_float();actual=c.intensity;assert abs(expected-actual)<.01,(path,expected,actual)
                value=expected
            else:raise AssertionError('Unexpected captured property: '+path)
            rows.append({'actor':a.get_actor_label(),'property':path,'value':value})
    return rows
for combination in itertools.product(*choices.values()):
    combo=dict(zip(choices,combination))
    for group,name in combo.items():assert manager.switch_on_variant_by_name(group,name),(group,name)
    for group,name in combo.items():
        v=sets[group].get_variant_by_name(name)
        report['groups'].setdefault(group,{})[name]=check_variant(v)
    report['combination_tests'].append({'choices':combo,'passed':True})
for group,name in {'Paint':'Mineral Teal','Glass':'Clear','WindowTrim':'Obsidian','Lighting':'Beauty'}.items():assert manager.switch_on_variant_by_name(group,name)
E.set_metadata_tag(lvs,'AssetCredit',(ROOT/'CREDITS.txt').read_text(encoding='utf-8-sig').strip())
E.set_metadata_tag(lvs,'BlueprintUsage','Reference YU7_VariantManager LevelVariantSetsActor; Switch on Variant by Name; groups Paint, Glass, WindowTrim, Lighting. Stable native scene actor bindings in Studio_YU7.')
E.save_loaded_asset(lvs);unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
report['verified_combinations']=len(report['combination_tests'])
report['garbage_collection_before_test']=True
(OUT/'variants.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
RESULT={'choices':choices,'verified_combinations':report['verified_combinations'],'total_captured_properties':sum(len(rows) for g in report['groups'].values() for rows in g.values())}
