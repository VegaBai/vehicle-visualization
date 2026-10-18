# Development history

记录规则：每次有实质决策、开发、验证、失败或 workaround，及时追加记录，注明原因、文件、证据和待办。未测试的工作不得写成完成。项目运行时功能优先 Blueprint；Python 仅用于编辑器资产制作与验证，不作为运行时依赖。除非没有可用接口或 workaround，否则不使用 C++。

## 2026-10-16 · 既往工作补录

以下内容依据本次会话、已有资产和检查报告补录，不代表当时已建立日志。

- **作品方向**：汽车 visualization 求职作品；用户熟悉 Unreal，每周可投入 40 小时，希望结合 AI/ComfyUI 加速制作。因 Tesla 车模成本，主车改用 Ddiaz Design 的 Xiaomi YU7。
- **授权与署名**：用户提供 CC BY-NC-SA 4.0 署名，已保存根目录 `CREDITS.txt`，必须原样加入最终 UE Credits。署名不等于无限制商业或 AI 使用许可。
- **原始资产保护**：`art/FINAL_MODEL` 保持不变；处理产物独立保存于 `art/YU7_UNREAL`。24 个原始文件的 SHA 检查一致，证据见 `art/YU7_UNREAL/reports/source_manifest.json` 和 `final_validation.json`。
- **Blender MCP 处理**：导入 121 个网格；统一比例、地面中心枢轴、变换和轴向。成车约 4.999 × 2.138（含后视镜）× 1.591 米；保留原模型比例，不宣称 CAD 尺寸精度。
- **几何和 UV**：保留作者自定义法线与有效 UV；8 个缺 UV 网格补 UV，582 个退化 UV 三角形局部修复，删除 8 个零面积面，修复方向不一致的方向盘面及一处极薄仪表台三角形。两处无法恢复原贴图布局的材质采用明确命名的 UVFallback 纯色材质。保留重叠/镜像 UV，无唯一光照 UV1，面向 Lumen/Path Tracer。
- **材质和纹理**：准备 35 个 PBR 材质、25 张 PNG，保留有效镂空遮罩，生成轮胎 DirectX/OpenGL 法线。材质是基础验证版本；原始贴图含烘焙阴影，车漆/玻璃仍需后续 lookdev。
- **导出与回读**：产出 `YU7_Prepared.blend`、`YU7_Unreal.fbx`、`materials.json`、`README_UE.txt` 与审计报告；FBX 回读为 121 网格、322100 顶点、579282 三角形；最大顶点误差约 2.20e-7 米、角点法线误差约 0.439 度。该结果仅为 Blender/FBX 验证，不等于 Unreal 验证。
- **UE 导入辅助脚本**：`art/YU7_UNREAL/import_into_unreal.py` 已生成并通过语法检查，之前尚未在 UE 执行。计划保留法线/切线并启用全精度 UV，避免微小 UV 修复在半精度转换时退化。

## 2026-10-16 · UE 导入与验证

### 01 · 建立持续记录与实现约束

- **用户要求**：后续每一步决策或开发均记录；复制当前汽车示例地图、导入 YU7，验证比例、法线和材质；功能采用 Blueprint，尽量避免 C++。
- **实施**：将规则写入根目录 `AGENTS.md`，新增本日志并补录既往过程。
- **决策**：使用现有 UE Python Editor Script Plugin 批量创建/检查资产，Blueprint 承载场景车辆；不新增 C++ 或运行时 Python 依赖。

### 02 · 确认项目环境（进行中）

- 已确认运行中的编辑器为 UE 5.8，项目路径 `VehicleStudio/VehicleStudio.uproject`；PythonScriptPlugin 已开启。
- 项目已有白色/黑色汽车摄影棚地图，启用 Lumen、硬件光追及 Substrate；静态光照关闭，与本资产的 UV0 工作流相符。
- 下一步读取当前编辑器世界和未保存状态，复制当前地图后再导入。磁盘设置显示最近地图为 `Studio_White`，仍需编辑器现场确认。

### 02a · UE Save Map 行为确认

- 第一次任务成功另存地图，但 UE 5.8 的 `save_map` 不会自动切换活动世界。保护性断言中止了后续导入，尚未修改原地图或创建车辆资产。
- 调整为另存后显式 `load_map` 打开副本；使用已生成的副本继续，避免重复创建。错误证据：`reports/ue_jobs/02_duplicate_import.json`。

### 03 · 当前地图副本

- 编辑器实测原地图为 `/Game/Studios/Levels/Studio_White`，10 个 Actor，无未保存地图或内容。已用 UE Save Map 另存为 `/Game/YU7/Maps/Studio_YU7`，后续仅编辑副本。原地图 SHA256 已记录至 `ue_original_map_hash.json`。
- 批处理通过现有 Python 编辑器插件执行，临时任务队列仅读取本工作区文件，不开启网络监听，结束后关闭。
- 导入采用显式 FbxFactory，临时关闭本次会话的 Interchange FBX 路由并在完成/异常后还原，以保证法线和分件设置生效；项目配置不变。

### 04 · Clear Coat 编辑器接口 workaround

- 导入已创建纹理，但材质阶段发现 UE 5.8 Python 不提供 MP_CUSTOM_DATA_0/1。原脚本中止，未导入几何。
- 改用 Make Material Attributes 的 ClearCoat/ClearCoatRoughness 引脚；保留真实 Clear Coat 着色，无需 C++。仅在本次新建的 YU7 专用目录恢复导入、重建未完成材质；不改样例资产。错误与恢复证据见 ue_jobs/03_load_import.json 及后续任务。

### 06 · Blueprint 车辆组装

- 创建 `/Game/Vehicles/YU7_Prepared/Blueprints/BP_YU7`，121 个 Static Mesh Component，共用地面中心枢轴；组件可用于 Sequencer，关闭无用途碰撞。未添加 C++ 或运行时脚本。
- 根据车头徽标在 UE 中的真实坐标校正 Blueprint 内部朝向为 +X，上方为 +Z；实测结果见 `ue_blueprint.json`。
- 在 `Studio_YU7` 放置 `YU7_Hero`，沿用示例车位置和旋转；副本内原示例车保留在 Reference/OriginalCar_Hidden，关闭显示/阴影。原地图和原资产不变。
- 原样署名写入所有网格与 Blueprint metadata、Actor tags；最终可见 Credits 仍是后续交付项，不能以 metadata 代替。

### 05 · 导入完成

- UE 5.8.3 内实际执行成功：121 个 Static Mesh、35 个材质，21 张实际引用纹理（准备包另含备用纹理）。材质按 manifest 重建，槽位全部关联。
- 每个网格关闭法线/切线重算、使用导入法线与切线、全精度 UV；未生成静态光照 UV。导入和构建日志未发现退化切线或材质编译错误。
- 证据：ue_jobs/05_resume_import.json。正在继续做 Blueprint 与实际渲染数据验证，导入成功不替代最终检查。

### 07 · 现场检查与编辑器恢复

- FBX 发出 6 条重复纹理节点名称提示，来自同一图片被多个材质引用；导入流程已关闭 FBX 自动材质/纹理生成，并按 manifest 逐槽绑定，后续检查所有实际引用。未发现退化法线/切线警告。
- 首次 Actor 包围盒包含编辑器默认图标，得到 256 cm 宽等错误测量口径；改用 Static Mesh 几何包围盒并排除编辑器图标。
- 关闭 Message Log 时 Alt+F4 意外触发整个编辑器正常退出（非崩溃）。所有产物已保存，日志确认正常退出；重新打开副本并进行持久性验证。后续不使用此快捷键关闭 UE 子窗口。

- 重开验证证实已保存的网格和材质可读取，但 UE 的 -ExecutePythonScript 命令行模式在脚本返回后会自动退出。改为普通交互启动，再从编辑器控制台启动临时任务队列；不使用该命令行模式保持交互会话。
- 将网格切线基底由默认 8 bit 提升到 16 bit，用于减少汽车高光反射的量化误差；完整审计将读取实际 Render LOD0 的每个三角形角点。

### 08 · 完整 UE 渲染数据审计与局部修复决策

- 所有 121 网格、35 材质槽位与实际引用纹理匹配；实测几何尺寸 499.89996 × 213.75048 × 159.10019 cm，最低点 Z=0，Actor Scale=1。原地图 SHA256 不变，项目无 Source/C++。
- 实际 Render LOD0 为 579252 三角形，比 FBX 少 30 个，来自 UE 构建时清理微小退化面。逐角点检查法线/切线/副切线：无缺失、无零向量、无非有限值；16 bit 基底最大单位长度偏差约 4.36e-5。
- UV0 检出 12 个零面积三角形（方向盘底部 11、后视镜底部 1）。初始报告 passed 字段仅表示法线/材质检查通过，UV 零面积另列；完整验收需修复后复检。
- 决策：仅局部调整上述 UE 资产的极小 UV，保留原始文件和外观；检查摄影机换到另一侧避开样例灯架遮挡。
- 改进临时任务队列的重入保护；发现 UE 保存操作可能触发嵌套 Slate tick，后续任务均待前一项完成后投递。

### 09 · UE 局部 UV 修复完成

- 从实际 Render LOD0 找出 12 个塌缩 UV 面，并按几何顶点位置匹配到 Source Model；仅在两个目标网格局部调整 UV，最大基准偏移 0.0002 UV（约 0.4 像素/2K）。
- 使用 UE 自带 Geometry Script 编辑器接口，无 C++，材质槽位保持；修复前后按三角形角点比较位置/作者法线，1e-5 精度完全一致。证据：ue_uv_repairs.json、ue_jobs/12_uv_repair.json。
- 这些为 UE 导入后修复；原始 FBX、准备 FBX/Blend 均未覆盖。重新导入 FBX 后需重跑验证及此局部修复步骤。

- 第一次 UV 复检仍有 7 面塌缩，均在方向盘底部。实际渲染 UV 仍为全精度浮点，但相邻角点在构建后被合并/复用；这不是半精度存储问题。提高剩余局部 UV 的间距至 0.002（约 4 像素/2K），使微小三角形在 UE 构建后保持独立。保留第一轮修复与审计报告用于追溯。

### 10 · 最终验收与保存

- 完整复检通过：121 网格、35 材质、21 引用纹理；Render LOD0 的 579252 个三角形逐角点检查法线/切线/副切线与 UV。零缺失或无效法线、零向量、非有限值、零面积 UV；所有材质槽和实际纹理关联匹配。
- 几何尺寸 499.89996 × 213.75048 × 159.10019 cm，底面 Z=0，Scale=1；已排除编辑器图标。Blueprint 重新编译成功，重开项目后 121 分件保持完整。
- 已实际查看 UE 前视、后视和 WorldNormal 预览；主要曲面法线过渡连续，车漆/玻璃/内饰/轮胎均使用预期材质。WorldNormal 中透明玻璃不写入常规 GBuffer，能看到内部，不代表玻璃丢失。预览为验收图，仍有实时光照噪声，不是最终作品镜头。
- 最终状态为打开 Studio_YU7、Lit 模式、正面检查机位并选中 YU7_Hero；所有新增资产和地图已保存。原 Studio_White 及原始模型/贴图 24 文件的 SHA256 全部保持一致。
- 署名原文已保存在根目录、准备包、UE 网格和 Blueprint metadata；最终屏幕 Credits 仍待后续 UI/成片制作，不将 metadata 误报为已完成 Credits。
- 本阶段没有 C++ 或运行时 Python 依赖。后续继续记录决策和开发；车漆、玻璃、内饰和灯光的最终 lookdev 留给作品制作阶段。
- 证据：reports/ue_validation.json、ue_session_final.json、ue_output_manifest.json 及三张 ue_*.png 检查图。

- 收尾确认：编辑器显示 All Saved，dirty_maps/dirty_content 均为空；临时编辑器回调已注销。新增 UE_IMPORT_REPORT.txt 汇总入口与验收结果，README_UE.txt/AGENTS.md 已更新；ue_blueprint.json 的包围盒字段明确标注包含编辑器图标，几何尺寸以最终审计为准。

## 2026-10-17 · YU7 材质、灯光与 Variant Manager

### 11 · 本阶段范围与工作方式

- 用户要求优先完成车漆、玻璃和广告感摄影棚灯光，并继续记录决策；使用 Variant Manager 管理外观切换。
- 先读取当前编辑器地图、未保存状态、实际组件材质、灯光和后期设置；保留导入基线、原模型和原 Studio_White。
- 计划新增参数化 lookdev 材质/实例和可比较的外观方案，利用原生 Variant Manager 记录组件材质与灯光属性。运行时继续 Blueprint 优先；Python 仅用于编辑器制作和检查，不引入 C++。
- 当前尚未修改 UE 资产或验证效果；本条记录的是实施范围。

### 12 · 检查结果与 lookdev 决策

- 当前地图确认是 Studio_YU7，未保存地图/内容均为空。Variant Manager 插件已启用，可用原生 API 创建变体并由 Blueprint 调用 Switch on Variant by Name。
- 现有车漆把 carPaint_Shape1 作为底色；新车漆使用独立色漆与 Clear Coat 层，避免旧贴图明暗影响新灯光。保留原始网格材质，采用场景 Blueprint 组件覆盖。
- 玻璃改用 Thin Translucent，将透射色与白色高光分开，独立设置车窗、天幕、灯罩；先做清透/烟灰两档供检查。
- 新建冷灰地台材质和含 6 盏 Rect Light 的灯光 Blueprint，分别控制主柔光、侧条、后轮廓、前补光、顶条和背景。原灯架隐藏并关闭影响；先保存 ImportBaseline 地图。
- 参数与效果仍需渲染验证；颜色为作品艺术方案，不声称是小米官方车漆色值。
- 依据：本地 UE 5.8 运行时接口反射；Epic Thin Translucent 文档 https://dev.epicgames.com/documentation/en-us/unreal-engine/using-transparency-in-unreal-engine-materials；Variant Blueprint 文档 https://dev.epicgames.com/documentation/en-us/unreal-engine/variant-manager-template-overview。

- 接口差异：UE 5.8 的 set_material_instance_scalar_parameter_value 在此工程中返回 False，但实际覆盖值已成功写入（Metallic 读回 0.150000006，覆盖数组存在）。取消将该返回值当成成败依据，改为逐项读回参数并比较；证据 ld03/ld04 任务报告。基线已保存，尚未动场景材质。

### 13 · 第一轮渲染发现与修正

- 首张 v1_teal.png 显示玻璃像不透明黑镜，黑塑料装饰还沿用白色导入底图。检查 UE 5.8 本地 SubstrateLegacyConversion.ush 证实：Thin Translucent 的根 Opacity 会把透射色插值到黑色；SurfaceCoverage 是独立输入。改为根 Opacity=0、Thin 输出 SurfaceCoverage=1，再由透射色调深浅。
- 新增带原 Alpha 遮罩的装饰材质，校正模型标为 BrilliantBlack 的白色轮眉/侧裙/窗框，以及深灰出风口。增加曜石黑/缎面金属材质供装饰变体使用；不覆盖原始材质。
- 主灯缩窄并移位，降低侧光、顶条和前补光，略加大清漆粗糙度以控制硬亮斑。55 mm 新机位降低俯视程度。
- 摄影机接口 set_current_focal_length 不存在，改用可写属性 current_focal_length/current_aperture，ld08 读写与保存成功；ld06 的失败未覆盖旧机位。

### 14 · 高光控制与变体的组件重建问题

- 第二轮 v2_teal.png 已恢复玻璃透射，可见内饰；黑色装饰恢复，需继续柔化车漆和风挡上的矩形灯反射。
- 生成原创解析柔光箱渐变纹理 T_SoftboxDiffuser.png，用于 Rect Light Source Texture；降低矿物青的金属比例和边缘色变化，避免过强金属感。灯光参数写入 Blueprint 默认组件，并使用 editor property 持久化场景覆盖。
- Variant Manager 切换灯光时会重建 Blueprint 组件，缓存的旧组件引用造成第一轮验证误报。ld12 用切换后重新获取的组件确认灯光实际值正确；后续全部使用重新解析的组件验证。运行时不增加脚本或 C++。

### 15 · UE 崩溃恢复与顺序约束

- ld13 在灯光 Blueprint 重编译、组件重实例化后调用旧 Variant.SwitchOn 时触发 UE 内部 UObjectArray Index>=0 断言并退出。崩溃日志保存在 reports/lookdev/ue_crash_ld13.log；不将未完成任务标为成功。
- 导入基线、第二轮材质/地图、柔光箱纹理、新灯光 Blueprint 和矿物青参数已在崩溃前保存；变体资产尚未保存，恢复后可从干净的绑定重建。
- 改进制作顺序：先完成并保存灯光 Blueprint，再创建变体绑定；绑定建立后不在同一会话中重编译目标 Blueprint 后直接调用旧绑定。检查与切换都重新获取组件引用。
- 已从保存点重新打开 Studio_YU7；下一步检查保存结果，再重新创建和验证全部变体。没有改用 C++。

### 16 · 恢复验证与变体建立完成

- 重开后确认 121 个车身组件、全部新材质、6 盏灯及 5 张柔光箱贴图引用完整，保存的灯光参数正确。
- 重新创建并保存 /Game/YU7/Lookdev/Variants/LVS_YU7_Lookdev，场景 Actor 为 YU7_VariantManager。
- 4 组共 9 个变体：Paint（Mineral Teal / Pearl White / Graphite）、Glass（Clear / Smoked）、WindowTrim（Obsidian / Satin Metal）、Lighting（Beauty / Sculpted Contrast）。逐一执行全部 24 种组合，读取真实材质槽和灯光强度，全部通过；证据 ld15_variants_rebuild.json、lookdev/variants.json。
- 默认恢复 Mineral Teal + Clear + Obsidian + Beauty；后续渲染检查色漆、烟灰玻璃和高反差灯光效果。

### 17 · 跨帧验证失败，修正稳定性结论

- ld15 的 24 组合在单次任务内通过，但 ld16 下一次任务切换再次触发 UE 内部断言。上一条仅证明同一调用内的属性结果，不代表跨帧稳定；本条纠正这一限制。
- 阅读安装的引擎源码 PropertyValue.cpp：HasValidResolve 缓存 Blueprint 构造组件地址，在组件销毁后检查 IsValidChecked(Container) 可触发断言；短任务内旧对象尚存时未暴露。相关日志 ue_crash_ld16.log。
- 决策：保留原 Blueprint 和网格，参与外观切换的分件使用原生 StaticMeshActor 场景绑定；灯光使用原生 RectLight Actor 绑定。仍由原生 Variant Manager/Blueprint Switch on Variant by Name 调用，零 C++、零运行时 Python。仅变化的分件分离，其他部分保留在 YU7_Hero；旧分件隐藏，避免重复绘制。
- 后续验收必须包含跨任务调用、强制 GC 后切换、地图重载后切换。

- 自动审批曾以“已有编辑器、重复启动可能冲突”为由拒绝恢复命令。随后只读核查窗口和宿主进程，确认仅 CrashReportClientEditor 存在、没有 UnrealEditor；增加启动前进程数量检查后获准恢复。未绕过审批或并行启动编辑器。

### 18 · 稳定场景绑定完成

- 21 个可切换分件改用附着在 YU7_Hero 下的 StaticMeshActor；原 Blueprint 中对应组件仅在当前地图隐藏并关闭阴影，原 BP/网格文件不改。6 个灯光变为原生 RectLight Actor，灯光 Blueprint 保留作参考、其原组件停用。
- Variant Manager 现在记录 63 个属性，仍为相同 4 组 9 个方案。强制垃圾回收后重新执行 24 种组合，全部通过。原生组件的捕获路径使用友好显示名，验证器已改为按组件类型解析，避免把显示名误当内部对象名（ld19→ld20）。
- 下一步继续跨帧切换和保存后重载检查，不能仅以单任务测试代替稳定性验收。

### 19 · 保存后恢复与关卡重载限制

- 已实际检查三张 1920×1080 UE 预览，矿物青/珍珠白/石墨灰、清透/烟灰玻璃与两种灯光均产生预期差别；预览仍有实时 Lumen 噪声，未当作 MRQ 最终成片。
- 原生绑定通过跨任务切换与强制 GC 测试，但在 ld27 仅重载地图、保留同一已加载 LVS 缓存后，ld28 再次触发引擎旧组件地址断言。日志 ue_crash_ld28.log。故“地图重载后稳定”尚未通过，不作此承诺。
- 工作流补救：通过 UE 官方 EditorLoadingAndSavingUtils.reload_packages 在旧世界销毁前重载 LVS，清除非序列化缓存，再重载地图。该操作是编辑器准备步骤，不是运行时 Python。正常重启编辑器也会重新从磁盘加载资产。
- 已保存全部场景绑定，恢复启动有前置检查保证只有一个 UnrealEditor。

### 20 · 安全重载流程通过

- 重启持久性检查通过：21 个原生变体分件 + 原 BP 中 100 个可见部件；原灯光 Blueprint 的 6 个组件停用状态保存正确。
- ld31 先重载 LVS 资产（返回 True，无错误）再重载地图，Map Check 为 0 Error / 0 Warning。
- ld32 在新的地图中强制垃圾回收，再执行全部 24 种组合、检查 63 项捕获属性，全部通过。该验证覆盖安全重载流程，不代表 UE 的“只重载地图”缺陷已经修复。
- 提供 tools/ue_lookdev_reload.py 作为编辑器安全重载入口，使用方法和已知限制已写入 LOOKDEV_GUIDE.txt 与 AGENTS.md。
- 当前没有新增 C++，没有运行时 Python 依赖；UMG 按钮界面和最终片尾 Credits 仍为后续作品阶段的任务。

### 21 · 文件与场景最终核对

- 原导入目录 178 个 UE 资产 SHA256 全部不变，原 FINAL_MODEL 的 24 个文件及 Studio_White 地图哈希不变。保留 Studio_YU7_ImportBaseline。
- 活动渲染部件仍为 121 个唯一网格，无重复绘制；几何尺寸保持 499.89996 × 213.75048 × 159.10019 cm，未编辑法线/UV/几何。
- 当前新增 15 个材质/实例、1 个柔光箱纹理、1 个参考灯光 Blueprint、1 个 Level Variant Sets；6 个活动 RectLight。完整路径和灯光参数在 lookdev/final_audit.json。
- 材质与灯光预览已经实际查看，变体跨帧、GC、编辑器重启和安全地图重载验证通过；只重载地图的引擎限制保留明确说明。
- 最终审计 dirty_maps/dirty_content 均为空。默认恢复矿物青 / 清透玻璃 / 黑色窗框 / Beauty；后续收尾保存缩略图并停止临时任务回调。

- 收尾完成：3 个车漆方案已添加实际 UE 渲染缩略图，LVS 资产在 Variant Manager 中打开供检查；当前默认方案与地图均已保存，编辑器显示 All Saved。临时本地任务回调已注销，未新增网络监听。证据：ld35_finish.json、lookdev/session_final.json、lookdev/output_manifest.json。

## 2026-10-17 · 下一阶段评估（建议，尚未实施）

- **本次范围**：应用户要求阅读开发历史并提出下一步建议；核对 AGENTS.md、art/YU7_UNREAL/LOOKDEV_GUIDE.txt、reports/lookdev/final_audit.json 与 session_final.json，并实际查看 beauty_mineral_teal.png、beauty_graphite_contrast.png。本次未连接编辑器或重新执行 UE 验证，既有验证状态依据此前报告。
- **画面观察**：两张预览中前风挡和引擎盖存在抢眼的大块亮反射；石墨灰方案侧面、轮胎与下部细节偏暗，画面上方留白较多。此为截图的视觉评估，不将亮反射直接判定为曝光裁切或材质错误。
- **建议优先级**：先以矿物青制作一个作品封面级主镜头，围绕构图、反射形状、暗部层次完成精修，并通过 MRQ 静帧和短运动测试确定输出质量；随后扩展少量展示镜头，再接 Blueprint/UMG 外观切换、相机控制与可见 Credits。
- **待验证与边界**：尚无最终 MRQ 输出、运行时 UMG 或打包验证；编辑器跨帧/GC/安全重载通过不等于 PIE 或打包稳定。后续运行时应独立验证连续切换及退出重进，沿用现有原生 Actor 绑定；最终 Credits 必须原样显示 CREDITS.txt。以上为本次建议，未视为用户已批准实施，也未修改 UE 资产。

## 2026-10-17 · 矿物青 4K 主视觉与 5 秒运镜制作

### 22 · 授权范围与制作准备

- 用户已授权执行矿物青 4K 主视觉及 5 秒运镜测试，重点为高光、玻璃、暗部细节。计划先保存镜头制作基线，在独立镜头地图/材质实例上迭代，保留既有 lookdev 和原始资源。
- 使用既有 UE Python 编辑器任务接口准备资产、Sequencer 和 MRQ；最终相机动画与渲染依赖原生 UE 资产，不添加运行时 Python 或 C++。先检查未保存状态再修改。
- 普通沙箱 Get-Process 未发现 UnrealEditor，但 Computer Use 返回已有 VehicleStudio 主窗口和 Variant Manager；以后以现场窗口和编辑器返回状态核实，避免错误重复启动。项目 SequencerScripting 配置当前关闭，需要检查可用 API 后决定是否启用并安全重启。
- 当前仅完成环境读取，尚未调整画面或输出新的渲染。

### 23 · 独立镜头场景与第一轮调整

- hero01 确认 Studio_YU7 无未保存内容，运行中的 MovieSceneSequenceExtensions 可用，虽项目显式配置关闭 SequencerScripting，本轮无需重启/修改插件配置。hero02 已安全重载 LVS 后将当前图另存并打开 /Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero；镜头图中的 VariantManager 解除 LVS 引用，避免调用旧图绑定，原图和变体资产保留。
- 复制矿物青、清透玻璃、摄影棚地面实例到 /Game/YU7/Cinematics/Materials，36 处场景材质覆盖只引用新实例；记录 223 个原资源哈希于 reports/hero/protected_before.json，待最终复核。
- v1 调整主/侧/轮廓灯位置和尺寸，增加低位柔光补光，补光 specular_scale 为 0.15/0.2，属于镜头艺术控制；独立车漆降低金属比例、玻璃提高透射，65 mm 主机位收紧构图。实看 reports/hero/v1_preview.png：车侧及轮胎细节改善，玻璃可见内饰，风挡亮反射和构图仍需迭代，不视为最终验收。
- tools/ue_hero_sequence.py 创建 LS_YU7_MineralHero_5s：24 fps、120 帧，带前后 handles，约 7.5 度缓入缓出相机弧线和轻微推近；所有关键帧为原生 Sequencer 资产。序列创建成功尚不等于渲染验证。
- hero06 灯光读取因 Actor.is_hidden 接口不存在失败；改用 hidden editor property，hero08 成功。检查所列旧灯光 Blueprint 组件强度为 0、visible=False，7 个镜头原生灯有效。
- hero09 已提交首张 1080p MRQ 测试，8 空间采样、1 时间采样、64 引擎预热/32 渲染预热；尚未完成。采样和预热依据实际引擎 API 与 Epic 文档 https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-rendering-image-quality-settings-in-unreal-engine 。
- 本地未找到 FFmpeg；沙箱 pip 下载因 DNS 失败，获自动审批后下载 imageio-ffmpeg 0.6.0 到 tools/vendor，用于本次成片编码，不是 UE 运行时依赖。

### 24 · MRQ 首次输出与高光定位

- Hero_preview_v1 MRQ 完成，success=True、无 executor 错误，实际输出一张 1920×1080 PNG，用时约 27.7 秒；已查看图像，原生相机绑定在 PIE/MRQ 生效，目标点下移到 Z=45 后主体垂直位置改善。证据 reports/hero/Hero_preview_v1_status.json、mrq_preview_v1/Hero_preview_v1_0000.png。
- tools/ue_hero_diagnose.py 暂时逐项停用 Key、Roof、Rear、Side 并输出对照，完成后恢复强度。实看 without_Key_Softbox / without_Rear_Rim / without_Side_Strip：风挡主要强光带来自 Key，引擎盖/车顶大片亮斑来自 Rear，Side 提供有用的侧面曲面线条。
- v2 将 Key 移至远侧后上方并扩大柔光面积，将 Rear 移至车尾近侧，适量增加前部/低位补光；独立玻璃 Specular=0.4。方案参数保存在 adjust_request.json，执行及渲染验收待下一步确认。

- v2 实际预览显示扩大面积虽柔化边缘，却令风挡及后侧窗反射覆盖更大，未达到目标。保留失败对照 v2_preview.png；v3 保持布局，将 Key/Rear 分别降为 4000/5000 lm，由前/低位补光承担暗部照明，检验降低光源亮度后的玻璃和车漆层次。

### 25 · 画面收敛与 4K 输出启动

- v3 MRQ 16 空间采样预览成功，实际查看确认风挡反射亮度降低、内饰可见，引擎盖原大白斑消除，但车头顶部略暗。v4 增加宽幅顶部漫反射补光（SpecularScale=0，镜头艺术控制），前补光 65000 lm，尾灯降至 3000 lm，镜头改为 68 mm；完整数值见 reports/hero/v4_settings.json。
- v4 MRQ 抽样输出第 0、60 帧成功，无 executor 错误。已分别查看：前部、轮胎、刹车和侧面层次可读；风挡保留柔和反射并透出内饰；相机移动到中段仍保持全车入镜，未见此前的大面积白斑。末帧与完整时间连续性仍待正式序列检查。
- hero17 开始 3840×2160 主视觉 MRQ，64 空间采样/1 时间采样、无运动模糊，PNG + EXR，保留默认 UE tone curve；EXR 不是未调色的 raw scene-linear 输出。文件目标 renders/YU7_MineralHero/still，最终完成以 executor 和文件检查为准。

- 4K 主视觉 MRQ 已完成：success=True、executor 无错误，约 31.5 秒，实际 PNG 8.31 MB、EXR 19.51 MB。已查看整体图像，亮斑控制、玻璃透射、车侧及轮胎层次保持；分辨率/解码/原资源哈希待交付核验脚本统一检查。
- 4K 下引擎记录 ScreenProbeGather DownsampleFactor 从请求 2 自动约束到 8，以避免探针 atlas 超过最大 2D 纹理尺寸。核对本机 LumenScreenProbeGather.cpp 的 GetScreenDownsampleFactor 与 clamp 逻辑：这是引擎资源限制，不能宣称实际使用了请求值 2。本次最终图使用实际约束值 8，后续交付记录此设置限制。
- hero18 开始完整 5 秒 4K 运镜：24 fps、120 帧、1 空间×16 时间采样，motion blur override 0.25。保留无损 PNG 帧序列，编码 MP4 后将检查全部 120 帧、时长和解码；当前还在渲染，未标记完成。

- 已独立解码 4K PNG（实际 RGBA，3840×2160）及 EXR，未报告解码错误；当前核对 223 个受保护文件哈希全部不变。已查看运动序列第 0 帧，与主视觉照明/构图一致；完整运动仍在输出。
- 新增 art/YU7_UNREAL/HERO_RENDER_GUIDE.txt，列出镜头地图、序列、材质、MRQ 参数、重渲步骤、4K 探针限制及署名；AGENTS.md 增加入口。指南明确最终可见 UE Credits、交互 PIE/打包验收不属于本次已完成项。准备交付核验与编码脚本 tools/package_hero_delivery.py，待完整输出后执行。

### 26 · 完整运镜完成，交付核验进行中

- hero18 MRQ 完成：3840×2160、120 个 PNG 帧、24 fps / 5 秒，success=True、executor 无错误，渲染约 420.5 秒。实际查看第 0、30、60、90、119 帧，均为正确相机，全车完整入镜，玻璃可见内饰，车侧光带和暗部层次保持；当前是抽帧视觉检查，不声称逐帧人工播放验收。
- EXR 头验证为 RGBA half-float、PIZ 压缩，data/display window 均为 3840×2160；FFmpeg 完整解码单张无错误。前 60 帧的数值检查未见明显画面跳变，统计存 first_half_check.json，指标不能代替细微闪烁的视觉判断。
- 已开始 tools/package_hero_delivery.py：读取全部 PNG、验证连续帧号、编码 H.264 MP4、再完整解码 MP4 并核对时长/原资源哈希。尚未取得编码完成结果。交付目录已含原样 CREDITS.txt 和 README.txt。
- hero19 完成安全重载流程后，将继续检查保存后的镜头资产与 Map Check；不修改原 lookdev 的绑定方式或声明原生引擎重载缺陷已修复。

- 交付编码与文件验收完成：120 个连续 PNG 全部成功解码，尺寸均为 3840×2160；MP4 使用 H.264 CRF16 / yuv420p，大小 4,980,007 bytes。完整解码得到 120 帧、00:00:05.000000，dup_frames=0、drop_frames=0，无解码错误。报告 reports/hero/delivery_validation.json、encode.log、decode.log。原始帧未做外部修图，MP4 仅编码/色彩矩阵转换。
- 全片相邻帧平均像素差最大约 0.001443（归一化），出现在运动速度较高的第 64 帧；固定背景区域相邻平均亮度变化最大约 0.000219。结合 0/30/60/90/119 帧视觉抽查未发现明显跳变；这不等于对所有细微时域噪声的逐像素保证。
- 保存后预设审计先后发现两个读取接口问题：hero20 的 settings 属性不含专用 OutputSetting；hero21 的 get_output_setting 接口不存在。核对本机 MoviePipelinePrimaryConfig.h 后改为公开 get_all_settings()，仅修正审计器，未改渲染预设或重渲。完整复检结果待 hero22。

### 27 · 最终交付与收尾

- hero22 最终场景审计通过：保存后重载仍为 121 个唯一可见网格（21 个原生分件）、8 个镜头灯光、68 mm 相机；原生序列为 24 fps / 120 帧，每个变换通道 33 个关键帧。两个最终 MRQ 预设实际保存为 3840×2160、64×1 静帧与 1×16 运镜采样。dirty_maps / dirty_content 均为空，Map Check 日志为 0 Error / 0 Warning。证据 reports/hero/final_scene_audit.json、ue_jobs/hero22_final_audit.json。
- 最终播放器兼容性检查发现最初 MP4 的 H.264 头保留了 unknown primaries / transfer，虽然编码参数已请求颜色标记。使用 FFmpeg h264_metadata 做无重编码重封装，明确 BT.709 色度/矩阵、sRGB transfer、limited range。重封装出现 AVCC header 尾字节提示，后续完整解码成功、120 帧 decoded framemd5 与原始编码逐帧相同，时长精确 5 秒且无重复/丢帧；故未影响画面数据。原编码保存在 reports/hero/YU7_MineralTeal_5s_4K_before_color_tags.mp4。
- 最终 MP4 为 4,980,026 bytes；新 SHA256 和实际色彩标记已更新 delivery_validation.json。tools/verify_hero_color_tags.py 完成验证和交付文件替换；package_hero_delivery.py 同步加入显式 VUI 标记供后续使用，本轮没有重新编码原始帧。最终 CREDITS.txt 与 MP4 comment 保留用户原文；应用内可见 Credits 仍待后续完成。
- 所有 223 个受保护文件保持原始 SHA256，原 Studio_YU7 / Studio_White、既有材质和模型未被本轮修改。最终 PNG、EXR、MP4、无损帧序列与 README 位于 renders/YU7_MineralHero。准备恢复编辑器主机位并注销临时任务回调，完成结果以 session_final.json 为准。

- hero23 收尾成功：镜头地图与序列均已保存，dirty_maps / dirty_content 为空；恢复主机位视口，Content Browser 定位原生序列。10 个 Cinematics 文件的大小与 SHA256 写入 output_manifest.json，临时编辑器任务回调已注销，未添加运行时脚本。证据 reports/hero/session_final.json、ue_jobs/hero23_finish.json。本次 4K 主视觉与 5 秒运镜测试交付完成。

## 2026-10-17 · Git 仓库初始化与首次发布

### 28 · 发布范围与版本管理准备（当次记录）

- 用户明确要求将当前项目加入 https://github.com/VegaBai/vehicle-visualization.git，添加 Unreal 配套忽略规则并推送。只读检查确认本地尚无 Git 仓库；授权网络检查确认目标为 VegaBai 所有的空公开仓库，当前 GitHub CLI 身份有效，远端无 HEAD。
- 普通沙箱的 GitHub DNS 失败，gh auth status 同时误报凭据无效；在授权网络环境中重检通过，无需修改或重新登录凭据。未输出明文令牌。
- 新增 .gitignore：排除 Unreal 生成目录、IDE/Python 临时文件、tools/vendor 以及 renders 下可重建的 frames/still；保留 Config、Content、Build 资源、原模型、准备资产、验证报告、最终 PNG/EXR/MP4 和署名。原始渲染序列仅不纳入 Git，未删除本地文件。
- 新增 .gitattributes：UE 资产、模型、纹理和交付媒体使用 Git LFS；文本统一 LF，CREDITS.txt 明确禁用文本转换以保留原始字节。新增 README.md 说明克隆、地图入口、LFS、依赖恢复、绝对路径及既有验收边界，不修改 UE 资产或运行时功能。
- 初步盘点：art 约 0.17 GiB、renders 约 0.97 GiB、tools 约 0.08 GiB、VehicleStudio 约 0.37 GiB；已安装 Git LFS 3.7.1。下一步初始化、检查暂存范围/大文件/敏感凭据及源文件完整性，再提交推送；此时尚未提交或上传。

- 本地 git init -b main 成功；随后 git lfs install --local 因沙箱禁止写 .git/config 而失败，尚未暂存文件。改为授权通道执行仓库本地配置和暂存，不修改全局 Git 配置。忽略规则抽查、模型/地图 LFS 属性及 CREDITS 禁用转换检查通过；首次凭据签名扫描无匹配（不等同完整安全审计）。

### 29 · 首次提交前验证（当次记录）

- 已完成本仓库 local Git LFS 配置、origin 关联和暂存；分支 main。597 个文件：VehicleStudio 293、art 239、tools 54、最终 renders 5、根目录 6。361 个文件使用 LFS，逻辑总量约 438.79 MiB（相同内容可能去重）。普通 Git 暂存对象最大 942,442 bytes，没有将大型资产直接塞入普通 Git。
- 检查暂存路径：Unreal 缓存、tools/vendor、原始逐帧/重复静帧输出均无泄漏；项目配置、uproject、Studio_White、工作地图、独立镜头地图、原始 FBX、准备 Blender 和最终 MP4 均已纳入。新增 .gitignore/.gitattributes/README.md 的 git diff --check 通过。
- 原始模型目录 24 个文件与 source_manifest.json SHA256 全部一致；hero/protected_before.json 所列 223 个受保护文件 SHA256 全部一致；三份 CREDITS.txt 的暂存 blob 与工作区原始字节一致。源资产未改写。
- Git 暂存提示文本 CRLF→LF 为 .gitattributes 的预期转换，不涉及模型或地图。以上仅为版本管理/文件完整性验收；本次未启动 UE、未重新执行渲染/PIE/打包测试。下一步创建初始提交，执行 LFS fsck 并推送，远端成功仍待实际结果。

### 30 · 首次远端发布与活动日志处理（当次记录）

- 初始提交 4dc3088fc5a712bb01cfdfd1eb63e4b9007b8c79 已成功推送 origin/main；git lfs fsck 返回 OK，上传成功为 340/340 个去重对象，约 446 MB（425.15 MiB），对应 361 个 LFS 文件。GitHub 默认分支为 main；git ls-remote 返回 SHA 与本地初始提交一致，后续 LFS dry-run 无待推送对象。
- 首次推送后的工作区检查发现 art/YU7_UNREAL/reports/blender_host_stdout.log 被现有 Blender 后台服务继续追加 get_addon_info 等运行消息。该文件不是稳定的验证报告，继续跟踪会造成持续无关修改；未停止后台服务或改写其活动日志。
- 将当前活动日志复制为 art/YU7_UNREAL/reports/archive/blender_host_stdout_2026-10-17.log 留存快照，并仅对原活动路径添加 .gitignore 例外、从 Git 索引移除；本地原文件保留。其他历史报告/崩溃日志仍跟踪。补充 *.log 的 LF 属性及 README 说明。
- 本条记录的是已完成的初次上传核验与随后发现的日志整理；日志整理及本记录将通过后续普通提交同步，原始提交不重写，不使用 force push。

## 2026-10-17 · 车身四边形线框方案讨论

### 31 · 曲面展示方向与现有拓扑核查（当次记录；尚未实施）

- 用户希望增加 quad 外观的 wireframe，避免 tri-poly 对角线，主要用于表现车身曲面。本轮提供方案建议；没有创建或修改 Blender/UE 模型、材质、地图或镜头。
- 读取 LOOKDEV_GUIDE.txt、README_UE.txt、HERO_RENDER_GUIDE.txt 及最近开发记录。汇总 art/YU7_UNREAL/reports/import_audit.json：121 个源导入部件的 polygons 与 triangles 逐件相等，合计均为 579,290；该历史审计表明导入源已三角化，不应把 UE 中隐藏对角线描述成恢复原始 quad 拓扑。此数是修复前源导入统计，与准备资产 579,282、UE 实际 579,252 三角形的阶段统计区分；本轮未重新读取 FBX 几何。
- 查询 Epic FBX Static Mesh Pipeline 文档，确认 UE 渲染网格需三角化：https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine 。Blender 官方 Wireframe / Shrinkwrap / Triangles to Quads 搜索结果支持离线网格贴合和边线生成的候选工具；文档部分页面直接打开失败，未据此宣称已经跑通资产流程。
- 建议在车身外板上单独制作疏朗、经过人工布线控制的 quad 展示层，沿引擎盖、肩线、轮拱与车门曲面排列。将其边转为可渲染细线几何（或烘焙线条遮罩）后以普通表面材质显示，避免 UE 原生 wireframe 再次显示三角形对角线。它是为曲面阅读制作的展示网格，不宣称为原作者拓扑或 CAD 曲率证据。
- 当前建议优先试引擎盖与前翼子板：矿物青车漆叠加低亮度浅青/白线，玻璃和轮胎保留原效果；可用 Blueprint/材质参数控制开关、亮度及扫描揭示，避免新增运行时 Python 或 C++。仅属方案，未创建 Blueprint 或验证 4K 时域稳定性。
- 其他选择：专用 UV 上的程序网格更易调密度，但现有 UV 含重叠、镜像与局部 fallback，不能假定直接套用即可得到均匀曲面线；宽反射条纹可辅助观察曲面起伏。后续若进入实现，需另存工作地图和资产，检查贴合误差、接缝、遮挡、细线闪烁，并保护现有 lookdev/hero 资产与稳定绑定。

### 32 · 引擎盖与前翼子板 quad 线框试作开始（当次记录）

- 用户已授权在引擎盖与前翼子板制作矿物青车漆叠加稀疏 quad 线的第一版，并要求保留现有场景和模型。将使用 art/YU7_WIREFRAME、/Game/YU7/WireframeStudy 与 renders/YU7_WireframeStudy 独立输出。
- 已读取现有 lookdev/hero 指南、脚本及状态。现有 Blender MCP 正在打开 YU7_Prepared.blend，宿主仅一个 UnrealEditor 进程；准备使用既有编辑器而非并行启动。
- 创建 art/YU7_WIREFRAME/reports/protected_before.json，记录 357 个既有模型、纹理、UE 内容文件的 SHA256。保护快照为本轮新生成，最终需复核。
- 采用离线采样贴合的细线几何，作为独立普通静态网格叠加；不改原车身拓扑、法线、UV 和材质。展示线网将另存，不宣称还原源拓扑。Python 仅用于编辑器准备与验证，无运行时依赖，尚未生成或验证最终效果。

- UE 编辑器确认当前为已保存的 MineralHero 地图、无脏内容。另存 /Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy 并先清 LVS 缓存再加载副本成功；尚未导入线框。原镜头、Lookdev 及导入模型不编辑。

- 线框 v01 采用引擎盖参数曲线与前轮中心极坐标曲线，两组交叉线形成 quad 外观；射线采样仅接受指定车漆外表面，边界/缺失位置断开，防止跨越灯孔和轮拱。生成三个独立细线网格，线宽 1.5 mm，中心表面偏移 1.1 mm，详见 art/YU7_WIREFRAME/reports/geometry_v01.json。输出仅位于新的准备目录；原 Blender 用 copy=True 保留。后续仍需 UE 贴合/渲染检查。
- 准备期间默认 python 命中不可访问的 Windows Store 别名，保护快照改由已连接 Blender Python 执行成功。Blender MCP 调用不共享局部变量，首次二次采样因 bs 未定义失败，改为每次显式构建 BVH 后成功；没有改原模型。

- wire03 已完成三个网格导入/材质/Actor 组装，但相机接口 set_current_focal_length 不存在而中止；未重跑一次性导入。修正为公开 current_focal_length/current_aperture 编辑器属性，通过 ue_wire_cameras.py 只续建相机和两个原生序列，已保存成功。仍待渲染验收。

- 线框 v02 改进：MRQ v01 成功输出整体与近景，但实际画面线条偏黑，轮拱有线头越界。v02 根据每个角度探测真实轮拱与肩部边界，将弧线与径向线共用端点，生成完整 quad 格。线宽仍 1.5 mm，中心偏移 1.1 mm；输出为新 FBX/Blend，v01 留存，未修改车身。几何指标见 reports/geometry_v02.json，待 UE 新预览。

- 线框 v03 改进：MRQ v02 两视图成功，亮度 100 在棚内 EV9/bias+1 下呈浅青白，未改变车漆。近景发现自动外边界受通风口影响出现折线；改用测量有效范围内的平滑解析轮拱边界，减少为三条弧线/两排 quad，13 条径向线共用端点，避开通风口凹槽。输出新版本，不覆盖 v01/v02，待 UE 渲染确认。
- v03 线条已导入独立版本目录并仅替换副本中的三个 overlay Actor。Blender 当前已另存并切换到 YU7_QuadStudy_v03.blend，v01/v02 展示集合隐藏，防止后续手动保存误覆盖 YU7_Prepared.blend。Final_v03 开始两张 3840×2160 / 64 空间采样 MRQ 输出；尚未完成最终图像验收。

- Final_v03 MRQ 两张 4K 静帧完成，success=True、无 executor 错误，耗时约 84.85 秒。已分别查看整体/近景：线条呈浅青白，轮拱曲线平顺，无三角形对角线，保持原车漆高光。文件解码和 357 个受保护文件哈希检查通过，两个 sidecar 署名与根 CREDITS.txt 字节一致。
- wire10 保存后重载审计发现线条组件碰撞枚举未持久化，当前已使用组件 modify + NoCollision 命名 profile 重设并显式保存地图；本次只修正碰撞，不改视觉资产，既有渲染仍有效。需重新加载复核后才能标记场景验收完成。

- wire12 重载后 NoCollision 已通过，但发现初次 attach_to_actor 未成功。日志证实原因是线条 Static 组件不能挂到 Movable 的 BP 根；先前“已附着”的描述仅是脚本意图，本条纠正。参照已有稳定分件流程，将三个新线条组件设为 Movable 并使用 KEEP_WORLD 附着，检查返回值/父级并保存；不修改原 BP，后续必须重载复查。

- wire14 保存后安全重载审计全部通过：原 121 个唯一可见车身网格保留，三个 v03 线框组件附着正确、NoCollision、无投影，材质 native wireframe=False，两个 4K/64 采样预设保存正确，无脏地图/内容；357 个原文件哈希仍一致。增加 README 和 AGENTS.md 入口，保留失败记录。由于修正了组件 Mobility/附着，使用保存后的场景重新渲染 Final_v03_Confirmed 两视图，以此作为最终交付；当前仍在输出。

### 33 · Quad 曲面线第一版交付完成（当次记录）

- Final_v03_Confirmed 完成两张原生 UE 3840×2160 / 64 空间采样静帧，MRQ success=True、errors=[]，耗时约 84.50 秒。已分别查看最终整体/近景，线条沿引擎盖和前轮拱排列，避免 v02 通风口牵动的折线，车漆/玻璃/灯光保持原观感；未做 AI 修图或外部合成。
- tools/yu7_wire_validate_files.py 成功解码两张最终 PNG，核对 357 个原模型、纹理和 UE 资产 SHA256 全部不变，署名 sidecar 与根文件字节一致。证据 art/YU7_WIREFRAME/reports/delivery_validation.json。
- wire16 最终保存后安全重载审计成功：121 个原车身唯一可见网格、三个独立线条组件、正确父级与 NoCollision、native wireframe=False；两套最终 MRQ 预设为 4K/64 采样。Map Check 为 0 Error / 0 Warning，dirty_maps/dirty_content 均为空。临时编辑器任务回调已注销，视口恢复整体观察机位。证据 reports/final_scene_audit.json、ue_jobs/wire16_finish.json。
- 最终资产清单写入 reports/output_manifest.json；可编辑源为 YU7_QuadStudy_v03.blend，地图为 /Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy。最终图位于 renders/YU7_WireframeStudy/Final_v03_Confirmed；旧版本保留作迭代证据，使用说明与 AGENTS.md 已更新。
- 本次交付为静帧概念验证，无运行时 Python/C++。未测试扫描动画、运动时域闪烁或打包交互；最终应用内可见 Credits 仍是后续交付项，不以本次 sidecar/metadata 替代。

## 2026-10-17 · Quad 试作 GitHub 检查点与整车扩展

### 34 · 保存用户认可的局部效果（当次记录）

- 用户认可引擎盖/前翼子板 v03，并明确要求先提交 GitHub，再将线条连接并扩展至整车外壳。当前 main 基于 0b77d92；本次先保存已验收的独立 WireframeStudy、准备资产、渲染、工具和过程报告，不重跑一次性创建脚本。
- 重新执行 tools/yu7_wire_validate_files.py：两张最终 4K PNG 解码通过，357 个受保护源文件 SHA256 均未变化，MRQ 成功报告与精确署名字节通过。沿用之前保存后重载/Map Check 的验证结论，本次提交前未重新运行引擎渲染。
- 将当前活动 Blender stderr 日志复制到 reports/archive 留存，再停止跟踪活动路径（本地不删除），与此前 stdout 的处理一致，避免后续后台服务追加使检查点产生无关修改。推送结果待实际执行。

- 检查点 420a2c6 已提交并成功推送 origin/main。Git LFS fsck OK，新增 36 个去重 LFS 对象约 241 MB 上传完成；远端 main 与本地完整 SHA 一致，提交后工作区干净。此节点保存用户认可的局部 v03 效果，可独立回退。

### 35 · 整车连续 quad 展示层（当次记录）

- 使用新 art/YU7_QUAD_BODY、/Game/YU7/QuadBodyStudy 与 renders/YU7_QuadBodyStudy，保留已推送的局部试作地图和全部源资产。范围为车漆外壳及后视镜外壳，玻璃、灯具和轮胎沿用原效果；板缝不焊接原模型。
- 将两套局部参数布线替换为整车共用的封闭六面 quad 参数笼，通过外侧射线贴合原车表面。共用面边界保证不同区域线位一致，外部遮挡/材质筛选阻止线条穿过玻璃、轮胎与灯具。此为新方案，实际密度、端部变形及接缝效果尚待引擎预览判断，不宣称恢复源拓扑。
- Python 仅离线生成展示线几何和自动化编辑器；沿用普通 Unlit 材质及原生 StaticMeshActor，无新增运行时 Python/C++。当前先完成原文件保护快照和独立地图准备。

- 已建立 393 个既有模型/纹理/UE 内容/局部试作图像的保护快照。body02 将已保存的局部地图另存为 Studio_YU7_QuadBody，先清除 LVS 缓存后加载成功；原地图未覆盖。
- 整车 v01 离线生成成功，保留 121 个原对象，新增 Body/Mirror_L/Mirror_R 三个展示网格；共享笼细分 30×14×10，线径 1.5 mm、中心偏移 1.1 mm。外侧射线仅保留外部车漆与独立后视镜外壳，轮胎/玻璃/灯具将遮挡线条。数据见 art/YU7_QUAD_BODY/reports/geometry_v01.json；尚未完成 UE 视觉验收。

- body03 完成独立新材质实例、三个附着到 YU7_Hero 的 Movable/NoCollision 展示组件，以及 Overview/Detail/Rear 三个原生序列。旧三块线条仅在新地图中隐藏，原局部地图仍保留 v03。新网格共 939,536 渲染三角形（可见格子仍无对角线），导入完成时存在临时静态网格编译内存估算提示；后续考虑在曲率误差约束下简化采样，避免不必要的线几何成本。
- Preview_v01 已提交三视图 1920×1080/16 空间采样 MRQ，预览结果尚未验收。

- Preview_v01 三视图 MRQ 成功，errors=[]，约 90.28 秒。实际查看前侧整体与衔接近景：引擎盖至翼子板有连续共用线网，车门/后翼子板延续同一规则，玻璃和灯具保持原状；后侧图已输出，继续视觉复核。三张图文件解码与 393 项源文件保护验证通过。
- v02 保持相同可见布线，新增 0.1 mm 阈值的离线折线简化（同时考虑管线法线变化）；78447 个采样点保留 8480 个，FBX 另存 v02，旧 v01 保留。约束针对采样曲线，不宣称 CAD 误差认证。待 UE 4K 输出检查平滑度和线条贴合。

- v01 后侧图已复核，尾门、后保险杠和后翼子板都有连续 quad 线条，未出现极坐标式三角扇。v02 UE 导入成功，合计 99,932 三角形，比 v01 减少约 89.4%。
- v02 几何抽查在前翼子板靠车门处发现 4 条短线段跨越同一源对象的细缝，中点距最近源表面最大 4.19 mm。补充每段 1/4、1/2、3/4 位置的贴合检查，超过 1.6 mm 时分段，另存 v03，不覆盖 v02；这是消除悬空线桥的局部修正。
- body06 保存后重载审计因 Actor.is_hidden 接口不存在中止，未发现资产损坏。审计改为检查旧线组件持久化 visibility=False（直接决定显示），不调用不存在的 Actor 接口；需重新通过审计后才能宣称完成。

- v03 精确移除 4 条跨细缝短线桥。8480 个线中心及 24057 个段内点复核：最近源三角面距离最大 1.507 mm、平均 1.068 mm（中心设计偏移 1.1 mm），报告 geometry_fit_v03.json。该检查针对三角网格采样点，不等于连续曲面/CAD 保证。
- body07 新版本导入成功，保留 3 个正确附着的展示组件，合计 99,916 三角形。即将安全重载复检再进行最终三张 4K 静帧；原场景和材料保持不变。

- body08 保存后安全重载审计通过：121 个原车身唯一可见网格保留、旧局部线组件隐藏、三个 v03 线组件 Movable/NoCollision/父级正确，native wireframe=False；393 项受保护资产哈希一致，dirty_maps/dirty_content 为空。MAP CHECK 日志 0 Error/0 Warning。
- 开始 Final_v03 前侧、近景、后侧三张 3840×2160、64 空间采样静帧，使用安全重载后的已保存地图。最终效果与图片验证仍待实际输出。

- Final_v03 前侧整体与衔接近景已输出并实际查看：减量后曲线平顺，未见明显折线；引擎盖、肩部、前翼子板与车门线位连续，细缝修正后不再跨接小缺口。后侧最终图仍在渲染，暂未标记最终完成。

### 36 · 整车 quad 展示层交付与保存（当次记录）

- Final_v03 三张原生 UE 4K/64 空间采样静帧全部成功，MRQ errors=[]、耗时约 143.74 秒。前侧整体、引擎盖/翼子板衔接近景和后侧图均已实际查看，车门、后翼子板、尾门/保险杠和车顶边框形成连贯展示线；原矿物青车漆、高光、玻璃与场景保留。未进行外部合成或 AI 修图。
- tools/yu7_body_validate.py 验证三张 PNG 全部解码，尺寸均 3840×2160，393 个受保护文件 SHA256 全部一致；准备目录/渲染目录 CREDITS 与根文件字节一致。证据 reports/Final_v03_validation.json。
- body10 最终保存后安全重载通过：原 121 个唯一可见车辆网格、3 个 v03 新展示网格、旧局部线隐藏、正确 Movable/NoCollision/父级与无投影；三个最终 MRQ 预设保持 4K/64。Map Check 为 0 Error/0 Warning，dirty_maps/dirty_content 均为空，临时任务回调已注销，编辑器停在新地图整体机位。
- 最终资产/图像 SHA256 清单已生成 reports/output_manifest.json，入口与复用限制写入 README、AGENTS.md、art/YU7_QUAD_BODY/README_UE.txt。展示线不改变原拓扑；本轮只验证静帧和编辑器持久化，不宣称运动抗闪烁或打包测试。最终应用内可见 Credits 仍待后续完成。
- 在已推送的局部检查点 420a2c6 之后，将整车版单独提交，保留两个阶段的独立回退点。当前整车版本尚待实际 Git/LFS 推送核验。
