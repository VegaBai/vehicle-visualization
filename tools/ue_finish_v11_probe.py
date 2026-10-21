"""Read-only editor/API inventory; never rerun old preparation scripts."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/finish_v11'
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
seq=unreal.load_asset('/Game/YU7/TunnelFlow/RoofSmooth_v10/Sequences/LS_YU7_TunnelFlow_Smooth_v10_12s')
paint=[]
for a in A.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        for i in range(c.get_num_materials()):
            m=c.get_material(i)
            if m and 'MineralTeal' in m.get_name():paint.append({'actor':a.get_actor_label(),'component':c.get_name(),'slot':i,'material':m.get_path_name(),'visible':c.is_visible() and not c.get_editor_property('hidden_in_game')})
tracks=[]
for tr in list(seq.get_tracks())+[t for b in seq.get_bindings() for t in b.get_tracks()]:
    tracks.append({'class':tr.get_class().get_name(),'name':str(tr.get_display_name()),'sections':[{'range':[s.get_start_frame(),s.get_end_frame()],'channels':[{'name':str(c.get_name()),'type':c.get_class().get_name(),'keys':len(c.get_keys())} for c in s.get_all_channels()]} for s in tr.get_sections()]})
RESULT={'world':unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),'rendering':unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering(),'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'v11_exists':unreal.EditorAssetLibrary.does_directory_exist('/Game/YU7/TunnelFlow/FinishShowcase_v11'),'paint':paint,'tracks':tracks}
(O/'starting_state.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
(O/'api_probe.txt').write_text('\n\n'.join(str(getattr(unreal,n).__doc__) for n in ['MovieSceneScriptingDoubleKey','MovieSceneScriptingFloatKey','MovieSceneParameterSection','MaterialExpressionNoise','MaterialExpressionCollectionParameter','CollectionVectorParameter']),encoding='utf-8')
