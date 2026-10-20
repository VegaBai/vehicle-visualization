import unreal,json
from pathlib import Path
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);E=unreal.EditorAssetLibrary
post=next(a for a in A.get_all_level_actors() if isinstance(a,unreal.PostProcessVolume));cam=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='CAM_YU7_TunnelFlow').get_cine_camera_component()
arch=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Tunnel_Architecture')
rows=[]
for c in arch.get_components_by_class(unreal.InstancedStaticMeshComponent):
    rows.append({'name':c.get_name(),'material':str(c.get_material(0)),'count':c.get_instance_count()})
cfg=unreal.load_asset('/Game/YU7/TunnelFlow/RenderPresets/MRQ_Keyframes_v04_228')
d=next(s for s in cfg.get_all_settings() if isinstance(s,unreal.MoviePipelineDeferredPassBase))
RESULT={'multi_disabled':d.get_editor_property('disable_multisample_effects'),'bloom_quality':unreal.SystemLibrary.get_console_variable_int_value('r.BloomQuality'),'show_bloom':unreal.SystemLibrary.get_console_variable_int_value('ShowFlag.Bloom'),'post_enabled':post.get_editor_property('enabled'),'post_blend':post.get_editor_property('blend_weight'),'camera_blend':cam.post_process_blend_weight,'camera_bloom_override':cam.post_process_settings.get_editor_property('override_bloom_intensity'),'component_materials':rows}
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/post_probe.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
