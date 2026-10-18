"""Persist NoCollision as a named component profile in the study map only."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports'
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name()=='/Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy.Studio_YU7_QuadStudy'
rows=[]
for a in A.get_all_level_actors():
    if a.get_actor_label().startswith('YU7_Quad_'):
        c=a.static_mesh_component;row={'actor':a.get_actor_label(),'before':str(c.get_collision_enabled()),'profile_before':str(c.get_collision_profile_name())}
        a.modify();c.modify();c.set_collision_profile_name('NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        row.update(after=str(c.get_collision_enabled()),profile_after=str(c.get_collision_profile_name()));rows.append(row)
assert len(rows)==3
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy')
RESULT={'components':rows};(OUT/'collision_persistence_fix.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
with (ROOT/'DEV_HISTORY.md').open('a',encoding='utf-8') as f:f.write('\n- Final_v03 MRQ 两张 4K 静帧完成，success=True、无 executor 错误，耗时约 84.85 秒。已分别查看整体/近景：线条呈浅青白，轮拱曲线平顺，无三角形对角线，保持原车漆高光。文件解码和 357 个受保护文件哈希检查通过，两个 sidecar 署名与根 CREDITS.txt 字节一致。\n- wire10 保存后重载审计发现线条组件碰撞枚举未持久化，当前已使用组件 modify + NoCollision 命名 profile 重设并显式保存地图；本次只修正碰撞，不改视觉资产，既有渲染仍有效。需重新加载复核后才能标记场景验收完成。\n')
