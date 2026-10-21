YU7 · 流光塑形 / FLOW INTO FORM
艺术指导实现 v09 · UE 5.8.3 · 2026-10-19

当前状态
四项设计已在隔离副本实现：灯光塑形、两主五辅、隧道层次、单次扫描与镜头高潮。
720p/1080p预演、原生4K全长、七张4K预检帧和七张精选原帧均已完成。
全长最终输出3840×2160、24fps、288帧、12秒、8时域采样；MRQ用时650.00秒。
全部PNG/MP4完整解码通过，突发变暗检查无异常；已查看覆盖全部288帧的接触表
及重点全分辨率图。未声称实时播放器观看或用户已完成审美验收。
最终保存后安全重载通过，Map Check零错误/零警告，所有历史保护快照一致。
实际完成状态以 reports/art_direction_v09/ 中的状态、验证及交付清单为准。
原始设计 design/ART_DIRECTION_v09.txt 是实施前的历史规格；其中“未实施”描述
指设计交接当时。此次新 session 的实现记录见 DEV_HISTORY.md 第45节。

打开入口
地图：/Game/YU7/TunnelFlow/ArtDirection_v09/Maps/Studio_YU7_TunnelFlow_AD_v09
序列：/Game/YU7/TunnelFlow/ArtDirection_v09/Sequences/LS_YU7_TunnelFlow_AD_v09_12s
效果、环境 BP、材质、七条线网格和渲染预设均在同一 ArtDirection_v09 根目录。
保持历史 /Game/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow 为 v08。
重载前必须先关闭 LVS 编辑器并 reload LVS_YU7_Lookdev package，再加载地图；
可使用 tools/ue_ad_v09_audit.py 的已验证流程。不要只重载地图或设置 realtime=True。

运行结构
全部运行时运动由原生 Blueprint、Sequencer、材质节点及共享 MPC ShotTime 求值。
Python 仅用于编辑器资产准备、离线采样和媒体编码，无运行时 Python/C++。
12秒、24fps、288帧，40mm固定焦距，15m/s；保留原车辆/车轮原生轨道。
摄影机35→112度同侧环绕，9.0–9.5秒放缓，最后离开到后侧。
长条塑形 RectLight 随车并沿车身移动，9.15–9.3秒峰值为常态1.25倍。
前/侧/顶填充分别18000/10000/8000lm，新增塑形光2300lm，远侧轮廓1400lm。
这些是固定曝光下实际预演调节的结果；不应作为其它场景通用参数。
保持原矿物青、玻璃和原始121个唯一车辆网格；新车漆等待用户参考图。

灯光与环境
同机位隔离图证实原 RoofFill 造成前挡白块，SideFill 造成门板宽高光。
填充灯移动/缩窄/降能量，增加窄主光与较弱远侧光；未改玻璃/车漆掩盖问题。
粗黑横带来自 Tunnel_Lane 的两实例，新环境BP副本将其清零，保留道路及门架。
隧道灯带降至原0.65倍，侧灯带升至335cm，避开车顶轮廓。
新副本顶灯明确 pitch=-90 朝下（原 positional Rotator 产生了 roll=-90）。
路面原生粗糙度按低频纵向噪声在0.34–0.44变化；原雾量及固定曝光不变。

七条流线
prepared/YU7_RoofAirflow_AD_v09.blend/.fbx 为新几何，七条线分别导入。
主线是实际摄影机侧 lane5/6，直径5.2mm；其余五条3mm，青色且更低亮。
lane6主峰权重1、lane5为0.75，辅线0.25–0.30；扫描段辅线再乘0.65。
自由脉冲0.6Hz，4.5–4.75秒过渡到同一主光头；缓慢WPO独立分线传播。
新屋顶BP七个有效网格共92,400三角形；隐藏原继承组件，避免重复显示。
所有有效组件 Movable / NoCollision / 无投影，WPO、光追WPO和位移速度输出开启，
bounds_scale=1.5，材质位移上限25cm。旧v01/v08网格和材质不改。
世界尾迹仍不附着车辆。三套车身/镜壳quad仍为99,916三角形，后门完整。
所有效果是普通 Masked Unlit 材质，native wireframe关闭；不是源模型真实拓扑或CFD。

时间约定
车身UV实际u=(2.5-x)/5；屋顶路径UV跨11m，采用等价u=2.2*U-0.2。
主光头经过某u：frame=114+90*u；网格激活：frame=122+90*u，落后8帧。
0–35实体车；36起描形；122开始单次网格扫描；204光头到尾；212网格完成；
216–227完整车身网格和后肩高光；228起退场；240起网格由前至后渐暗；
264–287完整一秒无效果实体车。退场不产生第二次扫描，未扫区域保持不可见。
共享旧 MPC 定义只读，时间由新序列驱动，未添加独立 Material Time。

已完成验证
roof_clearance.json：96Hz、3,010,483个样本，转折处2cm空间间距，其余5cm；
计入管半径并包含全部121原车网格，静态最小15.90cm、动画最小13.46cm，
最大合成位移17.92cm。此为离散采样，不是连续碰撞保证。
camera_clearance.json：426个实际可见环境实例包围盒、96Hz/1153个时刻；
最小相机净距69.23cm，中心视线无交叉，角度单调。图像检查仍是必要补充。
native_cue_samples.json：关键帧原生MPC时间与15m/s位移符合序列。
scene_audit.json：安全保存后重载、121原网格、全部新绑定、完整后门、组件设置、
510项历史文件哈希、40mm焦距、署名metadata及无未保存包检查。
最终额外复核历史420项、71项以及v08清单13项，全部哈希一致。

交付文件（仓库根目录下 renders/YU7_TunnelFlow/ArtDirection_v09）
Final_r10_4K_12s.mp4：原生4K全长，无声；SHA256
bdfa5ef8845ab8ff80e4b1868146ff56fa855387fcfa29a65fdc4dcf76806264。
Previs_r08_1080p_12s.mp4：相同最终场景的独立原生1080p观看预览。
01_CleanPaint_AD_v09_4K.png 至 07_FinalFrame_AD_v09_4K.png：
从最终连续序列的24/96/122/163/222/269/287帧逐字节复制，无修图/合成/放大。
Keyframes_r09_4K目录：正式全长输出前的七张原生4K预检帧。
Final_r10_4K_Review目录：接触表与细节条带，只用于检查，非原生交付静帧。
output_manifest.json记录3份视频、7张精选原帧、7张预检帧及87个新资产/源文件；
视觉检查依据与局限见visual_review.json，媒体尺寸/署名/保护验证见实际报告。

过程证据与复用
reports/art_direction_v09 与 renders/YU7_TunnelFlow/ArtDirection_v09 保存本轮记录。
Diagnosis_r01 因同队列地图未正确切换而无效；r02按单地图逐轮诊断，r03定位标线。
r04为中断后部分场景，r05灯光过亮；r06修正后进入r07/720p与r08/1080p全长预演。
不要把失败诊断当作最终版本，也不要盲目重跑任何一次性 prepare/effects/scene/
scene_resume/sequence/Blender脚本。它们记录精确开发步骤，不是通用幂等安装器。
可复用 ue_ad_v09_render.py，但必须无活动MRQ并用新的输出名/预设名，避免覆盖。
完整原生帧是可重渲本地中间件；保留精选原帧、MP4、Credits和全部验证记录。

署名与剩余项目交付项
本轮视频旁 CREDITS.txt 必须与根文件逐字节一致；新序列 Attribution metadata
以及MP4 comment保存用户原文。应用内可见Credits、打包与新机器验证仍待最终
项目交付；sidecar和metadata不替代应用内Credits。当前为无声镜头。
