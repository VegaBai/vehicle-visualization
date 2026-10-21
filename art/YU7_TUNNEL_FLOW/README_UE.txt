YU7 · FLOW INTO FORM / 流光塑形
2026-10-19 · 原生 UE 5.8.3 镜头

当前状态
v09艺术指导已在后续新session的隔离副本实现，入口和操作规则见 README_AD_v09.txt。
新根目录 /Game/YU7/TunnelFlow/ArtDirection_v09；原v08工作地图与全部历史成果保留。
720p/1080p预演、原生4K全长及七张精选原帧均已完成，全部PNG/MP4完整解码通过。
当前成片：renders/YU7_TunnelFlow/ArtDirection_v09/Final_r10_4K_12s.mp4。
最终安全重载/Map Check和历史510/420/71项及v08清单保护通过；本轮无声。
请以 reports/art_direction_v09/ 的实际状态及 DEV_HISTORY.md 第45节为准。

保留的v08状态
2026-10-19 脉冲/起伏修订：当前地图屋顶组件已覆盖为 M_TunnelRoofAirflow_Pulse_v02。
七条线具有错开的移动亮峰、缓慢呼吸，以及向后传播的上下/横向波动。
Previs_v08_1080p_12s.mp4 已完成 12 秒/24fps/288 帧，全部 PNG/MP4 完整解码通过，
整帧突发变暗检查无异常；关键时刻的脉冲位置、线条起伏与结尾淡出已实际查看。
两张原生 4K 图为 RoofPulse_v08_4K.png 和 RoofPulseFullBody_v08_4K.png。
本轮交付 1080p 全长预览与 4K 静帧，尚未渲染 v08 全长 4K；Final_v06 是旧版。
完成证据见 reports/Previs_v08_1080p_validation.json、pulse_output_manifest_v08.json
与 pulse_final_audit_v08.json。当前为无声版本。
上一版完整地图备份为 Maps/Studio_YU7_TunnelFlow_BeforePulse_v07。

v09设计交接的历史背景
design/ART_DIRECTION_v09.txt 已写明灯光塑形、两主五辅流线、隧道层次、
高潮节奏的具体规格、帧级 cue、验证标准和新 session 交接指令。
设计session仅写文档；后续新session已按该文档实施v09，详见 README_AD_v09.txt。
新车漆方向等待用户后续提供示意图，灯光修订先沿用现有矿物青。

上一版车顶气流输出
2026-10-17 车顶气流修订：工作地图已新增 BP_TunnelRoofAirflow_v01。
七条示意气流越过引擎盖、风挡、玻璃车顶和尾部，带有向后移动的亮段。
旧版地图备份为 Maps/Studio_YU7_TunnelFlow_BeforeRoof_v06；v06 电影保持原样。
Previs_v07_1080p_12s.mp4 已完成 12 秒/24fps/288 帧，全部 PNG 和 MP4 完整解码通过。
RoofAirflow_v07_4K.png、RoofFullBody_v07_4K.png 为本轮原生 4K 对照帧。
整帧突发变暗检查无异常，开场关闭、顶部覆盖、后门网格和末帧无遮挡已实际复核。
本轮交付 1080p 全长预览和两张 4K 图，尚未重渲 v07 全长 4K；旧 Final_v06 是上一版。
完成证据见 reports/Previs_v07_1080p_validation.json、roof_output_manifest_v07.json。
本效果用于气流视觉表达，没有进行 CFD 仿真。

上一版输出
独立场景、原生动画、1080p 全长修正版和保存后重载已验证。
Final_v06_4K 已完成原生 3840×2160、24 fps、288 帧/12 秒输出，8 时域采样。
全部 PNG 与主 MP4 完整解码通过，突发变暗检查无异常。实际复核开场、
贴面光、网格扫描、9.5 秒完整前后门余辉及末帧无遮挡；420 项保护文件一致。
证据见 reports/Final_v06_4K_status.json、Final_v06_4K_validation.json。

打开入口
地图：/Game/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow
序列：/Game/YU7/TunnelFlow/Sequences/LS_YU7_TunnelFlow_12s
在 Sequencer 播放 0–287 帧，24 fps，共 12 秒。
SEQ_YU7_TunnelFlow 已引用序列，auto_play=False，避免编辑器/MRQ 重复启动。
后续应用可用 Blueprint 调用其 Sequence Player；本次未做打包交互验收。

镜头内容
车辆向世界 -X 行驶，15 m/s（54 km/h），12 秒共 180 m。
摄影机同侧由前侧 35° 弧移到后侧 115°，40 mm 固定焦距；高度约 1.1–1.45 m。
1.5 秒开始贴面光路；约 3.1 秒开始逐步显现世界空间尾迹。
4.7 秒主光头重新从车头走向车尾；5.05 秒开始单次 quad 扫描，约延后 0.35 秒。
9 秒抵达车尾；亮峰停留至 9.6 秒，再于 10.2 秒前衰减。
已扫描区域保留 15% 相对余辉，包含前后车门、后翼子板与尾门。
10.2 秒起从前往后淡出，约 11.75 秒结束；车辆持续前进，末帧不切黑。
当前为无声画面版；设计文件中的声音建议尚未制作。

可编辑资产
Blueprints/BP_TunnelArchitecture：428 个静态网格实例，其中两条可选道路标线隐藏，
以及 32 个照明组件。保留石墨隧道、门架、纵向灯带和微粗糙路面。
Blueprints/BP_TunnelWheel_FL/FR/RL/RR：每套复用六个原车轮网格。
轮轴按 38.2397 cm 半径生成原生 Euler 转动关键帧；不使用物理模拟。
原 Hero 24 个对应轮部件仅在新地图隐藏，固定制动部件保留；原 121 个唯一网格
仍有且仅有一个可见版本。原 BP_YU7、源模型与历史地图均不修改。

Materials/MPC_TunnelFlow 的 ShotTime 是唯一效果时间源，序列原生 MPC 轨道驱动。
不要换为 Material Time，否则跳帧和 MRQ 预热会改变效果顺序。
M_TunnelGrid：三套完整 v03 quad 几何副本，UV.x 是车头到车尾的归一化坐标。
M_TunnelSurfaceFlow：沿车漆外侧射线贴合的纵向和轮拱光路，绕开非车漆区域。
M_TunnelWorldWake：独立世界空间轨迹，UV.x 编码发射时间，不附着车辆。
材质均为原生节点构成的 Masked Unlit，能量同时控制发光和像素丢弃，
clip=0.008。未扫描区域真正不可见，不留下黑色不透明管线。
网格材质另有 5.02–5.08 秒显式开启控制，避免车鼻在进度 clamp 边界提前显现。
两盏跟随光头移动的真实 PointLight 为漆面提供照明响应。
曝光固定 EV8、bias 0.6；Standard Bloom、低密度体积雾。

车顶气流修订
Blueprints/BP_TunnelRoofAirflow_v01：单个 Movable/NoCollision 网格组件，
Actor YU7_Tunnel_RoofAirflow 附着于 YU7_Hero，七条气流共 92,400 三角形。
Meshes/RoofAirflow_v01 与 Materials/M_TunnelRoofAirflow_v01 为新增资产。
曲线最小离车身约 15.75 cm，长 11 m，宽度 6 mm；覆盖玻璃上方的空间，
不用旧 CarPaint 射线筛选。它是车周稳定气流的示意路径，材质亮段沿路径向后流动。
ShotTime 仍驱动原生节点材质，1.4 秒开始显现，10.15–11.55 秒前后顺序淡出。
该高位流线附着车辆；旧独立世界空间 YU7_Tunnel_WorldWake 仍不附着车辆。
准备源 prepared/YU7_RoofAirflow_v01.blend/.fbx，制作脚本为一次性，勿盲目重跑。
reports/roof_scene_audit.json 同时检查原 420 项及 v06 新增保护的 58 项文件。

车顶脉冲与起伏修订（v08）
Materials/M_TunnelRoofAirflow_Pulse_v02 使用 MPC ShotTime 作为唯一时间源。
低底光 0.007、移动脉冲 0.68 Hz、分线呼吸 0.36 Hz，避免七条线同时闪亮。
原生 World Position Offset 叠加两组竖向波与一组横向波；近车顶幅度小，
向尾部逐渐增大，路径两端平滑归零。材质最大位移限制为 35 cm。
当前地图 RoofAirflow 组件启用 WPO、光追 WPO 和位移速度输出，bounds_scale=1.5。
覆盖只存在于工作地图实例；原 v01 Blueprint、网格、材质和 v07 媒体保持不变。
98,007 个离线时间/空间采样计入管线半径后的最小车体间距为 8.12 cm；
该结果是采样验证，不代表 CFD 或连续碰撞保证。实际外观以原生渲染为准。
报告 pulse_scene_audit_v08.json 检查保存后重载、原 420 项及额外 71 项文件保护。
ue_roof_pulse_prepare/apply.py 为一次性步骤，不要在已完成资产上盲目重跑。

准备源与保护
prepared/YU7_TunnelEffects_v01.blend 和 .fbx：五个新增效果网格，原模型保留。
三个网格副本与 QuadBody v03 顶点坐标相同，只改流向 UV，不代表恢复源拓扑。
原 WireframeStudy、QuadBodyStudy、MineralHero 和 Lookdev 地图保留。
420 项既有文件保护快照位于 reports/protected_before.json。
旧局部线、原摄影棚和原灯光只在当前地图隐藏；VariantManager 继续保持未绑定。

复用与排错
不要盲目重跑 ue_tunnel_prepare/assets/scene/sequence 或 Blender 几何创建脚本。
这些是一次性准备；resume/finish/refine 脚本只适用于开发记录中的精确中间状态。
Python 只用于编辑器准备和离线编码；无运行时 Python 或 C++。
重载前必须关闭 LVS 编辑器、先重载 LVS_YU7_Lookdev package 再加载地图；
tools/ue_tunnel_audit.py 执行了该过程。普通裸地图重载未获安全验证。
初期 Additive 材质在本场景 MRQ 不可见，最终改用经实测的 Masked 材质；
保留原光追玻璃设置。M_Debug_* 仅为诊断材质，未用于最终效果。

输出与证据
renders/YU7_TunnelFlow/Final_v06_4K/：原生 4K PNG 帧，不做 AI 修图或合成。
Final_v06_4K_12s.mp4：原生序列 H.264 主文件，已完整解码验证。
YU7_TunnelFlow_12s_1080p.mp4：主文件的轻量观看副本，已完整解码 288 帧。
01_CleanPaint 至 05_FadeOut 的 _4K.png：从原帧直接复制的五个关键时刻。
Previs_v03_720p_12s.mp4 为过程版本，存在车鼻提前露线和尾段相机遮挡。
Final_v05_4K 是主动取消的部分输出；以上均不作为最终交付。
Keyframes_v01/DebugMaterials/Keyframes_v02–v05 留作迭代证据。
报告包括 scene_audit.json、实际 MRQ 状态、完整媒体解码、保护文件哈希和输出清单。
请以最新 DEV_HISTORY.md 以及最终实际报告为准；没有打包或新机器验证。

署名
CREDITS.txt 与仓库根文件保持逐字节一致；也写入序列 metadata 和 MP4 comment。
最终应用内可见 Credits 仍待后续制作，sidecar/metadata 不替代该要求。
使用限制见根目录 CREDITS.txt 和 AGENTS.md。

2026-10-19 — Roof smoothing correction v10 completed
Current corrected shot: /Game/YU7/TunnelFlow/RoofSmooth_v10/Maps/Studio_YU7_TunnelFlow_Smooth_v10
See README_SMOOTH_v10.txt and reports/roof_smooth_v10/output_manifest.json. Native 4K full shot and 1080p preview are in renders/YU7_TunnelFlow/RoofSmooth_v10. Prior v09 assets and media are preserved.
