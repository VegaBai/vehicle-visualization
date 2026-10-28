"""Cross-frame native option validation, attachment check and historical preservation."""
import unreal,json,time,hashlib,itertools
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_ITASHA/reports/v01';D='/Game/YU7/Itasha_v01'
E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
actors={a.get_actor_label():a for a in A.get_all_level_actors()};hero=actors['YU7_Hero'];manager=actors['YU7_ItashaOptions'];lvs=manager.get_level_variant_sets(True)
assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name()==D+'/Maps/Studio_YU7_Itasha_v01.Studio_YU7_Itasha_v01'
parts=[a.static_mesh_component for a in actors.values() if a.get_actor_label().startswith('YU7_VP_')]
parts += [c for c in hero.get_components_by_class(unreal.StaticMeshComponent) if c.is_visible() and not c.get_editor_property('hidden_in_game')]
assert len(parts)==121 and len({c.static_mesh.get_path_name() for c in parts})==121
decal_actors=[a for a in actors.values() if a.get_actor_label().startswith('YU7_Itasha_') and isinstance(a,unreal.DecalActor)]
assert len(decal_actors)==5,len(decal_actors)
for a in decal_actors:
    assert a.get_attach_parent_actor()==hero
    assert a.get_component_by_class(unreal.DecalComponent).mobility==unreal.ComponentMobility.MOVABLE
paint_map={'Pearl White':'MI_Paint_PearlWhite','Graphite':'MI_Paint_Graphite','Mineral Teal':'MI_Paint_MineralTeal'}
cases=list(itertools.product(['None','Rengoku','Zenitsu','Giyu'],paint_map))*2
state={'status':'testing','cases':[],'errors':[],'active_meshes':121,'attached_decals':5,'runtime_python_required':False,'runtime_cpp_added':False}
path=O/'switch_audit.json';last=[0.];pending=[None];index=[0]
def write():path.write_text(json.dumps(state,indent=2),encoding='utf-8')
def stop():unreal.unregister_slate_post_tick_callback(unreal._itasha_audit['handle'])
def tick(delta):
    if time.monotonic()-last[0]<.3:return
    last[0]=time.monotonic()
    try:
        if pending[0]:
            choice,paint=pending[0]
            for a in decal_actors:
                expected='MI_Itasha_'+('Sweep_' if '_Sweep_' in a.get_actor_label() else '')+choice
                assert a.get_component_by_class(unreal.DecalComponent).get_decal_material().get_name()==expected,a.get_actor_label()
            count=0
            for c in parts:
                for i in range(c.get_num_materials()):
                    if c.get_material(i).get_name().startswith('MI_Paint_'):
                        assert c.get_material(i).get_name()==paint_map[paint];count+=1
            assert count==9,count
            state['cases'].append({'itasha':choice,'paint':paint,'passed':True});pending[0]=None;write()
        if index[0]<len(cases):
            choice,paint=cases[index[0]];index[0]+=1
            assert manager.switch_on_variant_by_name('Itasha',choice);assert manager.switch_on_variant_by_name('Paint',paint);pending[0]=(choice,paint)
        else:
            assert manager.switch_on_variant_by_name('Itasha','Rengoku');assert manager.switch_on_variant_by_name('Paint','Pearl White')
            initial=hero.get_actor_location();before={a.get_actor_label():a.get_actor_location() for a in decal_actors}
            hero.set_actor_location(initial+unreal.Vector(120,45,10),False,True)
            for a in decal_actors:
                d=a.get_actor_location()-before[a.get_actor_label()];assert abs(d.x-120)<.01 and abs(d.y-45)<.01 and abs(d.z-10)<.01
            hero.set_actor_location(initial,False,True)
            assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
            protected=json.loads((O/'protected_before.json').read_text());bad=[r['path'] for r in protected if hashlib.sha256((R/r['path']).read_bytes()).hexdigest()!=r['sha256']];assert not bad,bad
            assert E.get_metadata_tag(lvs,'AssetCredit')==(R/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
            assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages();assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
            unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'MAP CHECK')
            state.update({'status':'passed','protected_files':len(protected),'historical_hashes_match':True,'translation_attachment_test_passed':True,'asset_credit_exact':True,'dirty_maps':[],'dirty_content':[]});write();stop()
    except Exception:
        import traceback
        state['status']='failed';state['errors'].append(traceback.format_exc());write();stop()
handle=unreal.register_slate_post_tick_callback(tick);unreal._itasha_audit={'handle':handle,'tick':tick,'state':state};write()
RESULT={'scheduled_cases':len(cases),'cross_frame':True}
