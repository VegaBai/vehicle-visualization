"""Resume only camera preparation after the v01 focal setter API mismatch."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports';DEST='/Game/YU7/WireframeStudy'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()==DEST+'/Maps/Studio_YU7_QuadStudy.Studio_YU7_QuadStudy'
cameras=[]
for name,loc,target,lens in [('Overview',(-780,880,270),(0,0,55),68),('Detail',(-550,430,295),(-125,0,88),65)]:
    label='CAM_YU7_Quad_'+name;found=[a for a in A.get_all_level_actors() if a.get_actor_label()==label];assert len(found)<=1
    camera=found[0] if found else A.spawn_actor_from_class(unreal.CineCameraActor,unreal.Vector(*loc));camera.set_actor_label(label);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc),unreal.Vector(*target)),False);camera.set_folder_path('YU7/QuadStudy/Cameras')
    c=camera.get_cine_camera_component();film=c.filmback;film.sensor_width=36;film.sensor_height=20.25;c.filmback=film;c.set_editor_property('current_focal_length',lens);c.set_editor_property('current_aperture',8.)
    focus=c.focus_settings;focus.focus_method=unreal.CameraFocusMethod.DISABLE;c.focus_settings=focus
    path=DEST+'/Sequences/LS_YU7_Quad_'+name;assert not E.does_asset_exist(path)
    seq=T.create_asset('LS_YU7_Quad_'+name,DEST+'/Sequences',unreal.LevelSequence,unreal.LevelSequenceFactoryNew());seq.set_display_rate(unreal.FrameRate(24,1));seq.set_playback_start(0);seq.set_playback_end(24)
    bind=seq.add_possessable(camera);cut=seq.add_track(unreal.MovieSceneCameraCutTrack).add_section();cut.set_range(-48,48);cut.set_camera_binding_id(seq.get_binding_id(bind));E.save_loaded_asset(seq)
    cameras.append({'name':name,'sequence':seq.get_path_name(),'camera':camera.get_path_name()})
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'cameras':cameras,'lines':[{'actor':a.get_actor_label(),'mesh':a.static_mesh_component.static_mesh.get_path_name()} for a in A.get_all_level_actors() if a.get_actor_label().startswith('YU7_Quad_')]}
(OUT/'import_v01.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
with (ROOT/'DEV_HISTORY.md').open('a',encoding='utf-8') as f:f.write('\n- wire03 已完成三个网格导入/材质/Actor 组装，但相机接口 set_current_focal_length 不存在而中止；未重跑一次性导入。修正为公开 current_focal_length/current_aperture 编辑器属性，通过 ue_wire_cameras.py 只续建相机和两个原生序列，已保存成功。仍待渲染验收。\n')
