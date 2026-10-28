"""Exercise the native Blueprint options on real PIE actors, then end simulation."""
import unreal,json,time,itertools,traceback
from pathlib import Path
O=Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not level.is_in_play_in_editor();assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
state={'status':'starting','cases':[],'errors':[],'validation_driver':'editor Python only; native Blueprint inherited methods execute switching'}
cases=list(itertools.product(['None','Rengoku','Zenitsu','Giyu'],['Pearl White','Graphite','Mineral Teal']))
start=time.monotonic();last=[0.];pending=[None];i=[0];context={};path=O/'pie_audit.json'
def write():path.write_text(json.dumps(state,indent=2),encoding='utf-8')
def tick(delta):
    if time.monotonic()-last[0]<.4:return
    last[0]=time.monotonic()
    try:
        if not level.is_in_play_in_editor():
            if state['status']=='ending':
                state['status']='passed';write();unreal.unregister_slate_post_tick_callback(unreal._itasha_pie['handle']);return
            if time.monotonic()-start>30:raise TimeoutError('PIE did not start')
            return
        if not context:
            world=unreal.EditorLevelLibrary.get_game_world();assert world
            aa=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor);actors={a.get_actor_label():a for a in aa}
            manager=actors['YU7_ItashaOptions'];hero=actors['YU7_Hero']
            assert manager.get_class().get_name()=='BP_YU7_ItashaOptions_C'
            assert hero.get_class().get_name()=='BP_YU7_ItashaVehicle_C'
            assert all(not c.get_editor_property('receives_decals') for c in hero.get_components_by_class(unreal.StaticMeshComponent))
            decals=[a for a in aa if isinstance(a,unreal.DecalActor) and a.get_actor_label().startswith('YU7_Itasha_')];assert len(decals)==5
            for a in decals:assert a.get_attach_parent_actor()==hero
            context.update({'world':world,'manager':manager,'hero':hero,'decals':decals,'actors':actors})
            state.update({'status':'testing','world':world.get_path_name(),'blueprint_class':manager.get_class().get_name(),'nonpaint_receivers_disabled':True})
        if pending[0]:
            choice,paint=pending[0]
            for a in context['decals']:
                expect='MI_Itasha_'+('Sweep_' if '_Sweep_' in a.get_actor_label() else '')+choice
                assert a.get_component_by_class(unreal.DecalComponent).get_decal_material().get_name()==expect,a.get_actor_label()
            expected={'Pearl White':'MI_Paint_PearlWhite','Graphite':'MI_Paint_Graphite','Mineral Teal':'MI_Paint_MineralTeal'}[paint]
            count=0
            for a in context['actors'].values():
                if not a.get_actor_label().startswith('YU7_VP_'):continue
                c=a.static_mesh_component
                for slot in range(c.get_num_materials()):
                    if c.get_material(slot).get_name().startswith('MI_Paint_'):
                        assert c.get_material(slot).get_name()==expected;count+=1
            assert count==9
            state['cases'].append({'itasha':choice,'paint':paint,'passed':True});pending[0]=None;write()
        if i[0]<len(cases):
            choice,paint=cases[i[0]];i[0]+=1
            assert context['manager'].switch_on_variant_by_name('Itasha',choice);assert context['manager'].switch_on_variant_by_name('Paint',paint);pending[0]=(choice,paint)
        else:
            state['status']='ending';write();level.editor_request_end_play()
    except Exception:
        state['status']='failed';state['errors'].append(traceback.format_exc());write()
        if level.is_in_play_in_editor():level.editor_request_end_play()
        unreal.unregister_slate_post_tick_callback(unreal._itasha_pie['handle'])
handle=unreal.register_slate_post_tick_callback(tick);unreal._itasha_pie={'handle':handle,'tick':tick,'state':state};write();level.editor_play_simulate()
RESULT={'scheduled':12,'environment':'real PIE actors'}
