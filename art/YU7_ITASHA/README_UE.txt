YU7 ITASHA v01 — 炎柱 / 善逸 / 义勇
制作日期：2026-10-27（America/Los_Angeles）

当前状态
独立地图、三套角色图案、配色条纹、无图案选项与独立三色车漆已保存。
已通过安全重载后的24次跨帧切换和实际PIE的12种图案/车漆组合验证。
三款各3视角原生3840×2160/8时域静帧已完成，9张均实际打开检查；无视频重制。
最终文件、哈希与验证依据见reports/v01/output_manifest.json。

资产入口
/Game/YU7/Itasha_v01/Maps/Studio_YU7_Itasha_v01
/Game/YU7/Itasha_v01/Variants/LVS_YU7_Itasha_v01
/Game/YU7/Itasha_v01/Blueprints/BP_YU7_ItashaOptions
/Game/YU7/Itasha_v01/Blueprints/BP_YU7_ItashaVehicle

使用
打开独立地图，再打开LVS_YU7_Itasha_v01的Variant Manager。
Itasha组的三款角色卡片附真实上车缩略图；双击目标Variant缩略图切换。默认炎柱/珠光白。
Itasha组：None（无图案）、Rengoku（炎柱·赤炎）、Zenitsu（善逸·雷闪）、Giyu（义勇·水流）。
Paint组：Pearl White、Graphite、Mineral Teal；与图案独立组合。
Blueprint场景Actor YU7_ItashaOptions继承LevelVariantSetsActor：
Switch on Variant by Name，Variant Set Name填Itasha，Variant Name填上述英文准确值。
换车漆使用Variant Set Name=Paint，Variant Name=Pearl White / Graphite / Mineral Teal。
控制BP类默认LVS引用为空；地图实例显式持久化本地图LVS引用。新放置控制Actor必须指定相应LVS。
当前使用Variant Manager和Blueprint接口，尚未增加UMG运行时按钮界面。

实现
五个原生DecalActor（左右人物、引擎盖人物、左右配色条纹）附着YU7_Hero。
人物素材为官方原PNG，宽度1000像素；材质中按alpha边界调整UV和物理尺寸，源文件未编辑。
条纹由原生材质节点生成，无运行时Python/C++，角色层不发光，保留原车漆光照。
独立车辆BP的121个模板关闭receives_decals，21个已拆出的原分件隐藏；可见21个原生Actor与100个BP部件总计121个唯一网格。
9个原生漆面组件接收图案。原BP、网格、历史地图、v11媒体和根CREDITS保持不变。
Blueprint实例receives_decals覆盖在PIE重建时会恢复，因此在本轮复制BP模板中配置，不改原BP。
侧面贴花显式roll=+90，左右yaw分别-90/+90；不要回退到过程脚本中的-90。
贴花U沿本地Z、V沿本地Y；人物按alpha包围盒进行UV映射和对应尺寸缩放，避免人物拉伸。

安全重载
使用tools/ue_itasha_v01_reload.py，先保存并重载原lookdev和本轮LVS包，再重载地图；或重启编辑器。
不使用单独重载地图后继续复用旧LVS缓存。制作脚本为一次性/定向恢复，不能盲目重跑。

记录与媒体
reports/v01：场景检查、保护快照、过程失败、实际渲染状态及最终manifest。
references/kimetsu_v01：原PNG与来源哈希，未核实角色图的复用/分发许可；模型许可证不适用于角色图。
renders/YU7_Itasha_v01（仓库根目录下）：原生Unreal输出，Test_*是过程诊断，不等于最终效果。
Final_r08_Rengoku_4K：炎柱/珠光白；Final_r09_Zenitsu_4K：善逸/亮面石墨；Final_r10_Giyu_4K：义勇/矿物青。
每组Side、Beauty、Hood分别为侧面、前侧和引擎盖特写；PNG原样保留，没有离线合成贴图。
原图1000像素画布不等于4K贴图；棚拍真实高光会覆盖部分人物，引擎盖视图最明显。
根CREDITS.txt原文保留，并用于本轮署名sidecar；应用可见Credits和打包/新机器验收仍是最终项目交付项。
