import unreal,json
from pathlib import Path
D='/Game/YU7/TunnelFlow';E=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
post=next(a for a in A.get_all_level_actors() if isinstance(a,unreal.PostProcessVolume));s=post.settings;before={}
for i,color,size in [(1,(1.,1.,1.),.3),(2,(.5,.6,.65),1.),(3,(.2,.35,.4),3.),(4,(.1,.2,.24),10.),(5,(.05,.1,.14),30.),(6,(.02,.05,.07),64.)]:
    key='bloom%d_tint'%i;before[key]=str(s.get_editor_property(key));s.set_editor_property(key,unreal.LinearColor(*color,1));s.set_editor_property('override_'+key,True)
    key='bloom%d_size'%i;s.set_editor_property(key,size);s.set_editor_property('override_'+key,True)
post.set_editor_property('settings',s)
bp=unreal.load_asset(D+'/Blueprints/BP_TunnelArchitecture');S=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);L=unreal.SubobjectDataBlueprintFunctionLibrary
for h in S.k2_gather_subobject_data_for_blueprint(bp):
    c=L.get_object_for_blueprint(L.get_data(h),bp)
    if isinstance(c,unreal.InstancedStaticMeshComponent) and c.get_name()=='Tunnel_Lane_GEN_VARIABLE':c.set_visibility(False);c.set_hidden_in_game(True)
unreal.BlueprintEditorLibrary.compile_blueprint(bp);E.save_loaded_asset(bp)
arch=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Tunnel_Architecture')
for c in arch.get_components_by_class(unreal.InstancedStaticMeshComponent):
    if c.get_name()=='Tunnel_Lane':c.set_visibility(False);c.set_hidden_in_game(True)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'bloom_tints_before':before,'lane_geometry':'Hidden black strips seen in v04; use continuous asphalt and wall LEDs as road guides.'}
Path('C:/github2/vehicle_visualization/art/YU7_TUNNEL_FLOW/reports/bloom_refine.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
