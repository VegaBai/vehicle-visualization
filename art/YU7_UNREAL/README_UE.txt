YU7 Unreal 导入包
准备日期：2026-10-16

主文件
YU7_Unreal.fbx：121 个独立部件，579,282 个三角面，35 个材质。
YU7_Prepared.blend：Blender 5.2 工作文件，贴图已打包；保留独立部件和检查用灯光、相机。
Textures：23 张原贴图的 PNG 副本，加 2 张由轮胎高度图计算的切线法线贴图（GL/DX）。
materials.json：材质参数、贴图关联和每个部件的材质槽顺序。
import_into_unreal.py：可选 UE5 Python 导入助手，见下方说明。
CREDITS.txt：用户指定的完整署名原文；工作文件中也有同名文本和场景属性。
reports：导入审计、修复记录、FBX 回读验证、源文件 SHA-256、前后预览。

尺度与方向
Blender 中使用米，车头为 +X、上方为 +Z。所有部件共用车辆包围盒地面中心作为原点。
源 FBX 导入长度为 0.047395 米，统一等比放大 105.47490695 倍至车长 4.999 米。
处理后整体包围盒约为长 4.999、宽 2.137505（含后视镜）、高 1.591002 米。
模型保留原作者造型比例，没有把三轴分别拉伸成厂家尺寸，也未宣称具有 CAD 精度。
长度依据 2025 年款发布参数；车型参考：https://www.ithome.com/0/863/974.htm

完成的修复
1. 应用部件层级变换，统一尺寸、朝向和地面原点；清理命名并保留原始名称属性。
2. 保留原有自定义分离法线，仅修正方向盘局部面朝向；移除仪表台 8 个零面积面。
3. 为 8 个缺少 UV 的部件生成 UV0，修复 582 个退化 UV 三角形。
4. 仪表台一个极细三角形产生零切线，将一个顶点移动 0.1 毫米后切线验证通过。
5. 重新建立基础 PBR 材质，修正轮胎把高度图当底色、玻璃完全透明、非灯具错误发光等问题。
6. 保留灯具、亮黑塑料、风口的有效 Alpha 遮罩；去掉不应透明的内饰和金属材质的微弱 Alpha。
7. 复制贴图到输出目录，WebP 无损转为 PNG；轮胎高度图生成 GL 和 DirectX 法线副本。
8. 写入完整原始署名，并记录本次尺寸、几何、UV 和材质修改。原始模型与贴图保持不变。

UV 和材质的实际边界
原文件中 carPaint_2 部件完全没有 UV，原车漆/门内衬图集映射无法恢复。
此部件已补 UV，并分别使用 M_YU7_CarPaint__UVFallback 与 M_YU7_Int_DoorF__UVFallback 纯色材质。
原有有效 UV 和对称部件的共享/镜像布局保留。UV0 不保证互不重叠，不是 Lightmap UV。
没有创建 UV1；本包按 Lumen / Path Tracer 的汽车静态展示用途整理。若使用静态烘焙，另做唯一 Lightmap UV。
原贴图包含烘焙明暗，基础材质仍需结合最终场景进行车漆、灯光和玻璃美术调校。
没有生成驾驶骨骼、LOD 或碰撞体。

Unreal 手动导入建议
使用静态网格导入 YU7_Unreal.fbx，Import Uniform Scale = 1。
Convert Scene = On；Convert Scene Unit = On；Force Front XAxis = Off。
Combine Meshes = Off；Import Normals and Tangents；保留导入的法线和切线。
Generate Lightmap UVs = Off；Auto Generate Collision = Off；初次导入不启用 Nanite。
LOD0 Build Settings：Use Full Precision UVs = On；Use High Precision Tangent Basis = On；Recompute Normals / Tangents = Off。
使用全精度 UV 很重要，半精度量化可能让已修复的细小 UV 三角形再次塌缩。
按 materials.json 配置基础颜色、粗糙度、金属度、Clear Coat 和透明模式。
轮胎法线使用 T_YU7_Tyre_Normal_DX.png，关闭 sRGB，Compression = Normalmap，不再反转绿色通道。
FBX 不能可靠携带完整 Blender 节点图，特别是颜色乘法、Clear Coat 和玻璃；不能仅依赖自动生成材质。
所有网格使用同一原点，组装时各部件采用相同位置/旋转/缩放；灯光、地面和相机未导出到 FBX。
已在 Unreal 5.8.3 中完成导入，车长实测约 499.9 厘米，Blueprint 局部车头 +X、上方 +Z；见下方项目结果。
Epic 导入选项：https://dev.epicgames.com/documentation/unreal-engine/fbx-import-options-reference-in-unreal-engine

可选 Unreal 导入助手
在 UE5 启用 Python Editor Script Plugin 后，使用 Tools > Execute Python Script 执行 import_into_unreal.py。
脚本创建 /Game/Vehicles/YU7_Prepared 下的贴图、基础材质和独立网格，按材质槽关联，并启用全精度 UV。
若目标目录已存在，脚本会停止，不覆盖已有资产；可修改脚本顶部 DESTINATION 使用新目录。
脚本已在用户的 UE 5.8.3 中执行；Clear Coat 通过 Make Material Attributes 连接，以绕开未暴露的 Python 枚举。
本项目导入时临时使用传统 FBX 路由：Interchange.FeatureFlags.Import.FBX 0，完成后恢复。已有目录中的恢复逻辑仅用于本次新建资产，勿直接用于用户已有资产。
脚本不修改/保存当前关卡，也不自动创建最终屏幕上的 Credits；署名仅随资产元数据带入。

Blender / FBX 验证结果
已通过 Blender 5.2 -> FBX 7.4 -> Blender 回读验证。
部件数、顶点数、三角面数、材质槽名称及顺序一致；自定义法线方向校验通过。
未发现无效法线、无效切线、退化 UV 三角形或缺失贴图。
顶点位置最大往返误差约 0.000000220 米；详细证据见 reports/final_validation.json。
源目录 24 个文件的 SHA-256 与处理前一致。
前后视图已渲染检查，图像为素材验收预览，不是最终作品镜头。

Unreal 项目结果（2026-10-16）
项目：C:/github2/vehicle_visualization/VehicleStudio/VehicleStudio.uproject
地图副本：/Game/YU7/Maps/Studio_YU7
车辆 Blueprint：/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7；地图实例 YU7_Hero。
原 Studio_White 地图保持不变，SHA256 已复核；副本内原示例车保留在 Reference/OriginalCar_Hidden，关闭显示与阴影。
121 个网格组件，35 材质，21 张实际引用纹理；运行时全部为原生资产/Blueprint，无 C++、无 Python 运行时依赖。
实际几何包围盒：499.89996 × 213.75048（含后视镜）× 159.10019 cm，最低点 Z=0，Scale=1。
注意：Actor Bounds 会包含编辑器图标，不能直接当作车身尺寸。
UE Render LOD0 为 579252 三角形；UE 清理了原 FBX 中 30 个微小退化面。
导入后局部修复方向盘底部和后视镜底部共 12 个 UV 三角形；几何位置、作者法线和材质槽保持。
重新导入准备 FBX 后，需要先运行 tools/ue_validate_vehicle.py，再运行 tools/ue_repair_imported_uvs.py，随后复检。不要跳过此步骤或依赖默认半精度 UV。
实际渲染数据、材质关联与 UV 检查结果：reports/ue_validation.json；局部修复记录：reports/ue_uv_repairs_pass1.json、ue_uv_repairs.json。
检查摄影机：CAM_YU7_Front / CAM_YU7_Rear / CAM_YU7_Side。预览：reports/ue_front.png、ue_rear.png、ue_world_normals.png。
本阶段为资产导入与验收，车漆、玻璃、内饰和灯光仍需针对最终作品做 lookdev；不是最终成片。
所有关键决策、失败与 workaround 记录在项目根目录 DEV_HISTORY.md；后续开发继续追加。

署名原文（最终 UE Credits 必须包含；该最终 UI 交付项仍待完成）
"2025 Xiaomi YU7" (https://skfb.ly/pCSLu) by Ddiaz Design is licensed under CC Attribution-NonCommercial-ShareAlike (http://creativecommons.org/licenses/by-nc-sa/4.0/).

2026-10-17 Lookdev 更新：当前 Studio_YU7 已加入新车漆/薄玻璃/冷灰摄影棚和 Variant Manager。使用方式、稳定绑定结构与安全重载方法见 LOOKDEV_GUIDE.txt；报告在 reports/lookdev。原导入资产保持不变，导入时基线另存 Studio_YU7_ImportBaseline。
