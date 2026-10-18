"""Match parent mobility and verify overlay attachment keeps world positions."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization');OUT=ROOT/'art/YU7_WIREFRAME/reports';A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name()=='/Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy.Studio_YU7_QuadStudy'
hero=next(a for a in A.get_all_level_actors() if a.get_actor_label()=='YU7_Hero');rows=[]
for a in A.get_all_level_actors():
    if a.get_actor_label().startswith('YU7_Quad_'):
        c=a.static_mesh_component;before=str(a.get_actor_transform());a.modify();c.modify();c.set_mobility(unreal.ComponentMobility.MOVABLE)
        assert a.attach_to_actor(hero,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
        rows.append({'actor':a.get_actor_label(),'parent':a.get_attach_parent_actor().get_actor_label(),'before':before,'after':str(a.get_actor_transform())})
        assert a.get_actor_location().is_nearly_zero(.000001)
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy')
RESULT={'attachments':rows};(OUT/'attachment_fix.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
with (ROOT/'DEV_HISTORY.md').open('a',encoding='utf-8') as f:f.write('\n- wire12 重载后 NoCollision 已通过，但发现初次 attach_to_actor 未成功。日志证实原因是线条 Static 组件不能挂到 Movable 的 BP 根；先前“已附着”的描述仅是脚本意图，本条纠正。参照已有稳定分件流程，将三个新线条组件设为 Movable 并使用 KEEP_WORLD 附着，检查返回值/父级并保存；不修改原 BP，后续必须重载复查。\n')
