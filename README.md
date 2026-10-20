# Vehicle Visualization · Xiaomi YU7

基于 Unreal Engine 5.8.3 的汽车可视化作品项目，包含 YU7 资产准备、摄影棚外观变体、矿物青 4K 主视觉和 5 秒运镜、整车 quad 曲面展示线，以及 12 秒隧道流光镜头。

## 矿物青主视觉与 5 秒运镜

![Xiaomi YU7 矿物青摄影棚最终渲染，3840 × 2160](https://media.githubusercontent.com/media/VegaBai/vehicle-visualization/main/renders/YU7_MineralHero/YU7_MineralTeal_4K.png)

Unreal Engine 原生 4K 渲染。

[查看 / 下载 5 秒运镜视频（4K MP4）](https://media.githubusercontent.com/media/VegaBai/vehicle-visualization/main/renders/YU7_MineralHero/YU7_MineralTeal_5s_4K.mp4) · 3840 × 2160 · 24 fps · 120 帧 · 无声。

## 获取和打开

先安装 Git LFS，再克隆仓库：

```powershell
git lfs install
git clone https://github.com/VegaBai/vehicle-visualization.git
cd vehicle-visualization
git lfs pull
```

用 Unreal Engine 5.8.3 打开 `VehicleStudio/VehicleStudio.uproject`。模型、贴图、UE 资产及交付媒体由 Git LFS 管理；只有指针文件的下载不包含完整资产。

- 外观工作地图：`/Game/YU7/Maps/Studio_YU7`
- 独立主镜头地图：`/Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero`
- 整车 quad 展示地图：`/Game/YU7/QuadBodyStudy/Maps/Studio_YU7_QuadBody`
- 隧道流光镜头地图：`/Game/YU7/TunnelFlow/Maps/Studio_YU7_TunnelFlow`
- 保留的局部 quad 试作：`/Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy`
- 运镜序列：`/Game/YU7/Cinematics/Sequences/LS_YU7_MineralHero_5s`
- 车辆 Blueprint：`/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7`

## 目录

| 路径 | 内容 |
| --- | --- |
| `VehicleStudio/` | Unreal 项目、配置、地图、Blueprint、材质和资产 |
| `art/FINAL_MODEL/` | 保持原样的原始 FBX 和贴图 |
| `art/YU7_UNREAL/` | 准备好的 Blender/FBX、纹理、制作指南和验证报告 |
| `art/YU7_WIREFRAME/` | 引擎盖/前翼子板局部 quad 线框试作 |
| `art/YU7_QUAD_BODY/` | 整车连续 quad 展示层、指南和验证报告 |
| `art/YU7_TUNNEL_FLOW/` | 隧道镜头设计、效果准备源、指南和实际验证报告 |
| `tools/` | Blender/Unreal 编辑器准备及离线验证脚本 |
| `renders/YU7_MineralHero/` | 最终 4K PNG、EXR、5 秒 MP4 与署名 |
| `renders/YU7_QuadBodyStudy/Final_v03/` | 整车 quad 前侧、衔接近景、后侧三张 4K PNG |
| `renders/YU7_TunnelFlow/` | 12 秒流光/quad 接力视频与关键帧，完成状态见镜头指南 |
| `DEV_HISTORY.md` | 持续追加的决策、实施、失败与验证记录 |

`.gitignore` 排除 Unreal 的 `Binaries`、`DerivedDataCache`、`Intermediate`、`Saved`，以及 IDE 临时文件、Python 缓存和 `tools/vendor`。`Config`、`Content` 和自定义 `Build` 资源保留。MRQ 的 `frames/` 原始逐帧输出和 `still/` 重复输出保留在制作机器，不上传；重渲步骤见 [主镜头指南](art/YU7_UNREAL/HERO_RENDER_GUIDE.txt)。

## 继续制作

先读 [项目约定](AGENTS.md)、[导入说明](art/YU7_UNREAL/README_UE.txt)、[Lookdev 指南](art/YU7_UNREAL/LOOKDEV_GUIDE.txt) 和 [开发记录](DEV_HISTORY.md)。不要对已有资产盲目重跑一次性创建脚本。

整车 quad 效果见 [展示层指南](art/YU7_QUAD_BODY/README_UE.txt)。线条是独立的曲面展示几何，不代表恢复了原模型 quad 拓扑。原模型和原地图保留；玻璃、灯具、轮胎及饰条保持原观感。

隧道镜头见 [制作与复用指南](art/YU7_TUNNEL_FLOW/README_UE.txt)。原生 Blueprint 组件、Sequencer 和材质集合时间驱动前进、车轮、贴面流光、世界空间尾迹与整车网格接力。越过风挡和车顶的七条示意气流具有错开的亮度脉冲及向后传播的柔和起伏，后门完整参与扫描并保留余辉。v08 全长 1080p 预览已完整解码验证；各版本成片状态以 MRQ 和媒体验证报告为准。

使用变体后需要重载工作地图时，执行 `tools/ue_lookdev_reload.py`，或重启编辑器；只重载地图仍有 UE 5.8 缓存问题。两处导入后 UV 修复及其重导入要求见导入说明。原始 `Studio_White`、导入基线和源模型均保留。

运行时功能使用 Blueprint/原生 UE 资产；Python 仅用于编辑器准备和离线处理。部分制作脚本和已有渲染预设使用原制作机器的绝对路径，换机器使用前需检查路径并设置新的输出目录。本次上传不代表全新机器或打包运行验收。

如需运行离线媒体处理脚本，可在自己的 Python 环境中安装 `numpy`、`Pillow`，并恢复脚本使用的本机 FFmpeg 依赖（Windows）：

```powershell
python -m pip install numpy Pillow
python -m pip install --target tools/vendor imageio-ffmpeg==0.6.0
```

历史渲染、资产及场景验证见 `art/YU7_UNREAL/reports/`。最终应用内可见 Credits、运行时交互界面及打包验证仍待完成。

Blender 服务持续写入的 `reports/blender_host_stdout.log` 和 `blender_host_stderr.log` 仅保留在本地；检查点快照另存于 `reports/archive/`，其他历史验证日志照常纳入版本管理。

## 模型署名

以下为用户提供的原始署名，另存于 [CREDITS.txt](CREDITS.txt)：

"2025 Xiaomi YU7" (https://skfb.ly/pCSLu) by Ddiaz Design is licensed under CC Attribution-NonCommercial-ShareAlike (http://creativecommons.org/licenses/by-nc-sa/4.0/).

该署名对应 YU7 模型；本仓库未对所有第三方资源统一重新授予许可。模型加工记录见导入说明和开发记录。
