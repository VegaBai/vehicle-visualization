"""Build persistent Blueprint components, then place only in the copied studio."""
import json
import math
from pathlib import Path
import unreal

ROOT = Path('C:/github2/vehicle_visualization')
assert json.loads((ROOT / 'art/YU7_UNREAL/reports/ue_jobs/05_resume_import.json').read_text(encoding='utf-8'))['status'] == 'success'
DEST = '/Game/Vehicles/YU7_Prepared'
BP_PATH = DEST + '/Blueprints/BP_YU7'
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name() == '/Game/YU7/Maps/Studio_YU7.Studio_YU7'
assert not unreal.EditorAssetLibrary.does_asset_exist(BP_PATH), 'Blueprint exists; refusing overwrite'
meshes = [unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets(DEST + '/Meshes', recursive=True)]
meshes = sorted((m for m in meshes if isinstance(m, unreal.StaticMesh)), key=lambda m: m.get_name())
assert len(meshes) == 121, len(meshes)
logo = next(m for m in meshes if '005_carBonnetLogoBase_body' in m.get_name())
front = logo.get_bounds().origin
yaw_correction = -round(math.degrees(math.atan2(front.y, front.x)) / 90.0) * 90.0
bp = unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(BP_PATH, unreal.Actor)
assert bp
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
handles = sub.k2_gather_subobject_data_for_blueprint(bp)
root_handle = next(h for h in handles if isinstance(lib.get_object_for_blueprint(lib.get_data(h), bp), unreal.SceneComponent))

def add(parent, cls, name):
    handle, reason = sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent, new_class=cls, blueprint_context=bp))
    if str(reason):
        raise RuntimeError(str(reason))
    assert sub.rename_subobject(handle, name)
    component = lib.get_object_for_blueprint(lib.get_data(handle), bp)
    assert component
    return handle, component

geometry_handle, geometry = add(root_handle, unreal.SceneComponent, 'VehicleGeometry')
geometry.set_editor_property('relative_rotation', unreal.Rotator(0, yaw_correction, 0))
for mesh in meshes:
    handle, component = add(geometry_handle, unreal.StaticMeshComponent, 'Part_' + mesh.get_name().split('SM_YU7_')[-1])
    component.set_static_mesh(mesh)
    component.set_mobility(unreal.ComponentMobility.MOVABLE)
    component.set_collision_profile_name('NoCollision')
    component.set_editor_property('relative_location', unreal.Vector(0,0,0))
    component.set_editor_property('relative_scale3d', unreal.Vector(1,1,1))
    component.set_editor_property('component_tags', ['YU7Part', mesh.get_name()])
credit = (ROOT / 'CREDITS.txt').read_text(encoding='utf-8-sig').strip()
unreal.EditorAssetLibrary.set_metadata_tag(bp, 'AssetCredit', credit)
unreal.EditorAssetLibrary.set_metadata_tag(bp, 'PreparationNotes', 'Front +X, Up +Z, centimeters, ground-center pivot. UVFallback materials documented in source package.')
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp), 'Blueprint compile failed'
assert unreal.EditorAssetLibrary.save_loaded_asset(bp)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
original = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == 'SM_AutomotiveTP_Car')
vehicle = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH), original.get_actor_location(), original.get_actor_rotation())
assert vehicle
vehicle.set_actor_label('YU7_Hero')
vehicle.set_folder_path('YU7')
vehicle.set_editor_property('tags', ['YU7', credit])
for comp in original.get_components_by_class(unreal.PrimitiveComponent):
    comp.set_visibility(False, True)
    comp.set_hidden_in_game(True, True)
    comp.set_editor_property('cast_shadow', False)
original.set_actor_hidden_in_game(True)
original.set_folder_path('Reference/OriginalCar_Hidden')
assert len(vehicle.get_components_by_class(unreal.StaticMeshComponent)) == 121
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
actors.set_selected_level_actors([vehicle])
bounds = vehicle.get_actor_bounds(False)
RESULT = {'blueprint': BP_PATH, 'components': 121, 'geometry_yaw_correction': yaw_correction, 'source_logo_center_cm': [front.x,front.y,front.z], 'actor_rotation': str(vehicle.get_actor_rotation()), 'actor_bounds_including_editor_helpers_cm': [v*2 for v in (bounds[1].x,bounds[1].y,bounds[1].z)], 'actor_bounds_center_cm':[bounds[0].x,bounds[0].y,bounds[0].z], 'geometry_dimensions_reference':'See ue_validation.json; actor bounds include the editor billboard.', 'credit_metadata':credit}
(ROOT / 'art/YU7_UNREAL/reports/ue_blueprint.json').write_text(json.dumps(RESULT, indent=2), encoding='utf-8')
with (ROOT / 'DEV_HISTORY.md').open('a', encoding='utf-8') as log:
    log.write('\n### 06 · Blueprint 车辆组装\n\n- 创建 `/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7`，121 个 Static Mesh Component，共用地面中心枢轴；组件可用于 Sequencer，关闭无用途碰撞。未添加 C++ 或运行时脚本。\n- 根据车头徽标在 UE 中的真实坐标校正 Blueprint 内部朝向为 +X，上方为 +Z；实测结果见 `ue_blueprint.json`。\n- 在 `Studio_YU7` 放置 `YU7_Hero`，沿用示例车位置和旋转；副本内原示例车保留在 Reference/OriginalCar_Hidden，关闭显示/阴影。原地图和原资产不变。\n- 原样署名写入所有网格与 Blueprint metadata、Actor tags；最终可见 Credits 仍是后续交付项，不能以 metadata 代替。\n')
