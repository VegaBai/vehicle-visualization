import hashlib
import inspect
import json
from pathlib import Path
import unreal
ROOT=Path('C:/github2/vehicle_visualization')
OUT=ROOT/'art/YU7_UNREAL/reports'
report=json.loads((OUT/'ue_validation.json').read_text(encoding='utf-8'))
assert report['passed'] and report['zero_area_uv_triangle_count']==0, 'Audit must pass before finishing'
bp=unreal.load_asset('/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7')
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
all_actors=actors.get_all_level_actors()
vehicle=next(a for a in all_actors if a.get_actor_label()=='YU7_Hero')
front=next(a for a in all_actors if a.get_actor_label()=='CAM_YU7_Front')
original=next(a for a in all_actors if a.get_actor_label()=='SM_AutomotiveTP_Car')
assert all(not c.get_editor_property('visible') for c in original.get_components_by_class(unreal.StaticMeshComponent))
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
key=level.get_active_viewport_config_key()
level.set_level_viewport_camera_info(front.get_actor_location(),front.get_actor_rotation(),key)
level.set_level_viewport_fov(39.598,key)
unreal.AutomationLibrary.set_editor_viewport_view_mode(unreal.ViewModeIndex.VMI_LIT)
unreal.SystemLibrary.execute_console_command(vehicle,'r.HighResScreenshotDelay 4')
actors.set_selected_level_actors([vehicle])
unreal.EditorAssetLibrary.sync_browser_to_objects([bp.get_path_name()])
assert level.save_current_level()
oldmap=json.loads((OUT/'ue_original_map_hash.json').read_text(encoding='utf-8-sig'))
same_map=hashlib.sha256(Path(oldmap['Path']).read_bytes()).hexdigest().lower()==oldmap['Hash'].lower()
assert same_map
source=json.loads((OUT/'source_manifest.json').read_text(encoding='utf-8'))
source_checks={name:hashlib.sha256((ROOT/'art/FINAL_MODEL'/name).read_bytes()).hexdigest()==data['sha256'] for name,data in source.items()}
assert all(source_checks.values())
credit=(ROOT/'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
assert unreal.EditorAssetLibrary.get_metadata_tag(bp,'AssetCredit')==credit
manifest={str(p.relative_to(ROOT/'VehicleStudio')):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for folder in [ROOT/'VehicleStudio/Content/Vehicles/YU7_Prepared',ROOT/'VehicleStudio/Content/YU7'] for p in folder.rglob('*') if p.is_file()}
(OUT/'ue_output_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
RESULT={'map':'/Game/YU7/Maps/Studio_YU7','blueprint':bp.get_path_name(),'blueprint_compile_passed':True,'mesh_components':len(vehicle.get_components_by_class(unreal.StaticMeshComponent)),'original_map_unchanged':same_map,'original_source_files_unchanged':all(source_checks.values()),'source_file_count':len(source_checks),'credit_metadata_exact':True,'visible_final_credits':'pending final project UI/sequence','dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'cpp_source_added':False,'previews':['ue_front.png','ue_rear.png','ue_world_normals.png']}
with (ROOT/'DEV_HISTORY.md').open('a',encoding='utf-8') as log:
    log.write('\n### 10 · 最终验收与保存\n\n- 完整复检通过：121 网格、35 材质、21 引用纹理；Render LOD0 的 579252 个三角形逐角点检查法线/切线/副切线与 UV。零缺失或无效法线、零向量、非有限值、零面积 UV；所有材质槽和实际纹理关联匹配。\n- 几何尺寸 499.89996 × 213.75048 × 159.10019 cm，底面 Z=0，Scale=1；已排除编辑器图标。Blueprint 重新编译成功，重开项目后 121 分件保持完整。\n- 已实际查看 UE 前视、后视和 WorldNormal 预览；主要曲面法线过渡连续，车漆/玻璃/内饰/轮胎均使用预期材质。WorldNormal 中透明玻璃不写入常规 GBuffer，能看到内部，不代表玻璃丢失。预览为验收图，仍有实时光照噪声，不是最终作品镜头。\n- 最终状态为打开 Studio_YU7、Lit 模式、正面检查机位并选中 YU7_Hero；所有新增资产和地图已保存。原 Studio_White 及原始模型/贴图 24 文件的 SHA256 全部保持一致。\n- 署名原文已保存在根目录、准备包、UE 网格和 Blueprint metadata；最终屏幕 Credits 仍待后续 UI/成片制作，不将 metadata 误报为已完成 Credits。\n- 本阶段没有 C++ 或运行时 Python 依赖。后续继续记录决策和开发；车漆、玻璃、内饰和灯光的最终 lookdev 留给作品制作阶段。\n- 证据：reports/ue_validation.json、ue_session_final.json、ue_output_manifest.json 及三张 ue_*.png 检查图。\n')
# Stop exactly the temporary local callback that invoked this file.
for frame_info in inspect.stack():
    if Path(frame_info.filename).name=='ue_editor_jobs.py' and frame_info.function=='tick':
        unreal.unregister_slate_post_tick_callback(frame_info.frame.f_globals['HANDLE'])
        RESULT['temporary_editor_runner_stopped']=True
        break
assert RESULT.get('temporary_editor_runner_stopped')
(OUT/'ue_jobs/request.json').write_text(json.dumps({'id':'session_closed','stop':True}),encoding='utf-8')
(OUT/'ue_session_final.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
