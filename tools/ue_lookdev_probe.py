import unreal, json
from pathlib import Path
OUT=Path('C:/github2/vehicle_visualization/art/YU7_UNREAL/reports/lookdev')
OUT.mkdir(exist_ok=True)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def props(obj, names):
    d={}
    for n in names:
        try: d[n]=str(obj.get_editor_property(n))
        except Exception as e: d[n]='UNAVAILABLE: '+str(e)
    return d
report={'world':world.get_path_name(),'dirty_maps':[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()], 'dirty_content':[x.get_path_name() for x in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()], 'actors':[]}
for a in actors.get_all_level_actors():
    row={'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'components':[]}
    for c in a.get_components_by_class(unreal.ActorComponent):
        if isinstance(c,unreal.LightComponent):
            row['components'].append({'name':c.get_name(),'class':c.get_class().get_name(),'properties':props(c,['intensity','intensity_units','light_color','temperature','use_temperature','source_width','source_height','attenuation_radius','cast_shadows','indirect_lighting_intensity','specular_scale','mobility'])})
        elif isinstance(c,unreal.StaticMeshComponent):
            row['components'].append({'name':c.get_name(),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())],'visible':c.is_visible()})
    if isinstance(a,unreal.PostProcessVolume):
        row['settings']=props(a.settings,['auto_exposure_method','auto_exposure_bias','auto_exposure_min_brightness','auto_exposure_max_brightness','auto_exposure_apply_physical_camera_exposure','override_auto_exposure_method','bloom_intensity','vignette_intensity','color_saturation','lumen_scene_lighting_quality','lumen_final_gather_quality','lumen_reflection_quality','path_tracing_samples_per_pixel','path_tracing_max_bounces'])
    report['actors'].append(row)
(OUT/'before.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
names=['VariantManagerLibrary','LevelVariantSets','LevelVariantSetsActor','VariantSet','Variant','PropertyValue','MaterialExpressionThinTranslucentMaterialOutput','MaterialExpressionFresnel','MaterialExpressionNoise','MaterialEditingLibrary','RectLightComponent','PostProcessSettings','MaterialInstanceConstant','CineCameraComponent']
api={}
for name in names:
    cls=getattr(unreal,name,None)
    api[name]={'doc':getattr(cls,'__doc__','MISSING'),'methods':{n:getattr(getattr(cls,n),'__doc__','') for n in dir(cls) if not n.startswith('_') and callable(getattr(cls,n))}} if cls else None
(OUT/'api.json').write_text(json.dumps(api,indent=2),encoding='utf-8')
RESULT={'world':report['world'],'dirty_maps':report['dirty_maps'],'dirty_content':report['dirty_content'],'actors':len(report['actors']),'api':str(OUT/'api.json')}
