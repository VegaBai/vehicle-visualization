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

- 整车提交 eb2e4dca16e16dac56aeaa6aab208ece2dd609c4 已推送 origin/main，远端 SHA 核验一致；git lfs fsck OK，32 个新增去重 LFS 对象约 370 MB 上传完成。提交后工作区干净。前一局部节点 420a2c6 完整保留；此推送结果记录通过随后纯文档提交同步，不重写历史。

## 2026-10-17 · 隧道流光与 quad 接力镜头设计

### 37 · 镜头设计范围与方向（当次记录；尚未实施）

- 用户要求先设计汽车在隧道中向前行进、流光沿车身曲线形成拖尾，随后 quad 网格出现并从前往后跟随发光的镜头，目标为炫酷、高科技。当前仅设计分镜/节奏，不修改 UE 地图、模型、材料、序列或现有 Git 检查点。
- 已读取整车 quad 指南、矿物青 Hero 指南及最新交付记录；现有 v03 整车展示层与 121 个原部件作为后续制作基础。设计输出独立放在 art/YU7_TUNNEL_FLOW/design，精确署名复制到其上级目录。
- 拟定 12 秒/24 fps 单镜头「流光塑形」：同侧低机位追车，先展示矿物青实体曲面与前进感，再由表面光头及世界空间拖尾勾勒曲率，随后一次从车头到车尾的 quad 发光接力，最后收回至车漆并驶离。此为设计参数，尚未制作/验证运动渲染。
- 将使用内置 imagegen 以现有整车 UE 静帧为车辆外形参考制作四格概念分镜。概念图用于美术方向，不属于 UE 渲染证据，不保证像素级车型/网格一致；不替换原模型或已验收图片。暂不制作交互可视化，分镜和时间表足以评审本轮设计。

- 四格概念分镜已通过内置 imagegen 生成并复制为 art/YU7_TUNNEL_FLOW/design/storyboard_v01.png；原生 UE 整车前侧图仅作为车型/车漆参考。最终提示词保存为 storyboard_prompt_v01.txt，镜头完整规格为 SHOT_DESIGN_v01.txt。
- 已实际查看四格图，01.0/04.0/06.8/09.5 秒时间标识、矿物青/冰青配色、同向行进、曲面光路、后方拖尾与前后网格接力表达成立。概念图的网格比现有 v03 更密，早期帧有少量镜壳/车鼻残留线纹，路面也偏湿亮；这些不是引擎效果，最终必须按规格使用现有稀疏网格、严格关闭未激活线条并降低路面镜面感。偏差已记入 CONCEPT_REVIEW_v01.txt，不将 AI 图作为实现验证。
- 本轮只新增设计文本、提示词、概念图和精确署名；未改变 VehicleStudio 资产、模型或现有渲染，没有制作动画或运行运动测试。设计文件保留在工作区，未为尚待评审的设计追加 GitHub 提交。

### 38 · 已批准镜头的原生 UE 制作（当次记录）

- 用户确认按设计制作；同时采纳其关于概念图后门缺失网格的纠正。原生整车 v03 已包含后门，制作时不删减；9.5 秒前后门必须保留扫描后的低亮线框。
- 新工作范围为 art/YU7_TUNNEL_FLOW、/Game/YU7/TunnelFlow、renders/YU7_TunnelFlow 和新增 tools/ue_tunnel_*、tools/yu7_tunnel_*。先保护现有内容，复制完整车身研究地图；不改既有源模型与已验收地图。
- 采用原生 Blueprint 组件、Sequencer 关键帧与材质参数控制 12 秒单镜头；Python 仅编辑器资产准备。长尾优先使用可确定求值的世界空间烘焙轨迹，避免跳帧/预热时依赖不稳定的模拟历史。统一序列时间驱动扫描与流光，曝光固定，保留真实光源对漆面的响应。
- 现在开始 API/场景探查，随后制作 720p 全长预演；尚未实现或验证运动效果，声音仍为设计建议。
- 已保护 420 个既有内容文件，tunnel02 成功将完整车身地图另存为独立 TunnelFlow 地图，并按要求先清 LVS 缓存再加载。
- Blender 离线生成五个效果网格：三个 v03 线几何的坐标完全相同副本（只改流向 UV）、贴合车漆的六组纵向/轮拱光路和独立世界空间尾迹。保留全部 121 个原对象，输出 prepared/YU7_TunnelEffects_v01.blend/.fbx。光路在非车漆和缝隙处分段；这是几何生成结果，尚未完成 UE 外观验证。
- tunnel03 导入五个新网格成功，但 CollectionScalarParameter 不支持关键字构造，创建 MPC 参数时报错。改用空结构体加 set_editor_properties；专用续作脚本只继续空 MPC/材质创建，不重复导入或覆盖已有资产。
- MPC 的 scalar_parameters 只暴露为 editor property，直接 Python 属性读取也失败。续作断言已改用 get_editor_property；这两次失败均未改动原有资产。
- 材质初建在 ComponentMask 单输入连接处中止，UE 编辑接口要求空输入名而非 Input。已纠正单输入连接，只重建本轮未完成的 M_TunnelGrid 节点；不重复导入网格、不动任何历史材质。
- tunnel06 已保存全部九个原生节点材质和 MPC，末尾报告因 Unreal Array 不能直接 JSON 序列化而报错；报告单独转换 list 补写，不重跑资产创建。扫描材质使用 Additive，让未到区域零贡献且不留下黑色不透明管线；最终亮度和时域表现待渲染验证。
- 轮毂组装时缓存的原 Blueprint 组件在编辑器重建后失效（第二个车轮零件找不到）；现场探查确认 121 个组件仍在，只有首个轮标已隐藏且新轮 BP 只创建了一件。改为每次重新从 Hero 获取当前组件，定向续作该未完成轮 BP，其余已建效果 Actor 不重复创建。
- tunnel10 完成四套原网格轮组、Blueprint 隧道实例和照明；最后雾属性名不匹配而中止。引擎头文件表明应为 bEnableVolumetricFog，改用 enable_volumetric_fog，专用 finish 只补雾/摄影机与保存。
- tunnel11/tunnel12 完成独立场景和 12 秒/24fps 原生序列。车速 15 m/s（54 km/h），位移 180 m；四轮按 38.2397 cm 半径转动，摄影机同侧前侧至后侧连续弧移。428 个环境实例由 Blueprint 管理，世界空间尾迹未附着车辆。
- MPC ShotTime 由 Sequencer 原生参数集合轨道驱动；参数轨道使用 24000 tick/s（已查引擎实现），变换轨道使用显示帧。网格 5.05 秒启动、9 秒到尾部、保留 15% 残光、10.2 秒后前向后淡出；真实 PointLight 同步沿车身移动。
- 先渲染 1.0、4.0、6.79、9.5、11.5 秒五张 720p/8 时域采样关键帧，检查空间方向、后门覆盖、布光和未激活区域隐形，再进入全长预演。
- Keyframes_v01 原生 MRQ 五帧成功（13.77 秒，errors=[]）；实际查看 1.0/6.79/9.5 秒图发现运动、追车镜头和实体模型成立，但网格/表面光/尾迹均不可见，暂不通过效果验收。蓝色填充光也使矿物青偏蓝，车轮接地阴影偏弱。
- 开始分离诊断 MPC 时间求值、材质绑定和效果 Actor 状态；同时计划中性化主光并启用关键灯阴影。保留本轮图作为失败证据，不以 MRQ 成功等同视觉通过。
- 诊断确认 9.5 秒 MPC 实际值为 9.5，全部效果 Actor 可见、附着/位置正确；恒定自发光对照渲染显示 opaque 网格正常、additive 表面光仍不可见。因此当前采用原生 masked unlit 方案继续，不将未证明的根因写成结论。
- 三个效果材质改为能量同时驱动 Emissive 与 OpacityMask，clip=0.008，未激活区域真正丢弃像素；保留连续亮度衰减。该调整仍是可编辑原生节点，无 C++。
- 中性化三盏跟随填充灯，主灯启用阴影，扫描灯强度缩至 22% 避免漆面出现过大青色圆斑。DebugMaterials_v01 已查看：矿物青恢复、完整后门网格确认可见；这只是恒定材质诊断，不代表扫描时序验证完成。
- Keyframes_v02 五张原生关键帧成功（12.81 秒）。实际查看 4.0/6.79/9.5 秒：未扫描区域隐形，车头先显现，后门最终完整覆盖，世界尾迹可见，masked 方案成立。但余辉偏暗、流光提前过多且尾部亮峰过早消退。
- v03 提高线条亮度而保留 15% 相对余辉；将尾部亮峰停留至 9.6 秒再于 10.2 秒前消散；纠正 FBX V 翻转造成的 lane 相位偏移，将光头与网格间距恢复约 0.35 秒。道路边线略提亮。准备全长 720p 预演，尚未完成连续运动视觉复核。
- Previs_v03_720p 完整 288 帧 MRQ 成功（68.98 秒，errors=[]），全部 PNG 与 H.264 完整解码通过，24 fps/12 秒，420 个保护文件 SHA256 全部不变。视频已编码，但视觉检查发现 progress clamp 在启动前使车鼻 p≈0 区域提前出现几条网格，不能作为最终版本。
- 已在 OpacityMask 增加 5.02–5.08 秒独立开启控制；检查 PostProcess 发现继承的是 FFT Bloom 与 Ray Traced translucency。为本镜头改用可控的 Standard Bloom（0.65，threshold=0.7）；玻璃继续保留原光追透明设置，线条继续使用已验证的 masked 路径。未把透明模式的相关性宣称为 additive 故障的充分根因。
- 当前 Keyframes_v04 提升到 1080p/16 时域采样复查开场关闭、流光和尾部全车余辉，再进行最终全长输出。
- Keyframes_v04 四张 1080p/16 时域帧成功，开场无网格、9.5 秒前后门连续余辉已实际确认。路面细标线却呈不自然黑带，当前隐藏该可选几何，保留整片路面与两侧 LED 导向。进一步显式设置 Standard Bloom 各级 tint/size，避免继承摄影棚后处理的残留设置；这是当前镜头局部调整。
- Keyframes_v05 四张 1080p 原生图成功（25.03 秒）。已实际查看 9.5/11.5 秒：路面黑带消失，9.5 秒前后车门连续网格完整，尾迹有青色柔光；11.5 秒网格按前后顺序消退，实体车仍前进。保持当前视觉方案进入 4K 全片。
- 显式读取确认 BloomQuality=5、MRQ disable_multisample_effects=False；旧 Bloom 各级 tint 为普通默认值，未发现继承异常。此次调整是增强调光，并非已证实的故障修复。
- tunnel27 保存后清 LVS 缓存并重载审计通过：121 个原车辆唯一网格全部保留（轮组副本替代隐藏组件），四个可旋转轮 BP、五个效果组件、父级/NoCollision/Movable/无投影正确，线材质为 Masked 且 native wireframe=False。独立世界尾迹无车身父级。
- 24fps/288 帧序列和 MPC 时间关键帧持久化正确，精确署名 metadata 一致，420 个既有文件哈希不变；Map Check 0 Error / 0 Warning，dirty_maps/dirty_content 为空。现在提交 Final_v05_4K 原生 MRQ 全长（3840×2160，16 时域采样）；完成和视觉验收待实际结果。
- 追加检查 Previs_v03 全部 288 帧统计发现第 269、287 帧大幅变暗（287 mean=0.0418，帧差=0.1153），不是正常收束。原因定位为末段 1060 cm 拉远半径使摄影机 Y 进入/越过 950 cm 内壁；单独 11.5 秒关键帧不足以发现末帧遮挡。
- 主动停止尚未完成的 Final_v05_4K，保留已经输出的部分帧和取消报告，不将其标记为完整成片。后两秒半径收至 930 cm，再逐子帧检查墙体间距，并先渲染完整修正版预演。此为必要的连续镜头修复。
- v06 相机按 96 Hz 共 1153 个样本检查，Y 最大值低于 910 cm，距内壁有充分间距；尾部只修改拉远半径，车辆和效果无变动。新增整帧统计的突发变暗检查，补足先前仅解码/尺寸验证的不足。先输出完整 1080p/8 时域预演供复核；4K 同样采用 8 时域采样并保持原生分辨率，后续检查运动细线。
- 已实际查看 v03 第 269/287 帧，确认遮挡是摄影机贴近墙体导致的前景黑面；v06 子帧采样最大 Y=899.985 cm，与 950 cm 内壁间距约 50 cm。README/AGENTS 增加新镜头入口与复用约束；gitignore 只排除可重渲的完整原始帧目录，保留成片、精选关键帧和报告。
- Previs_v06_1080p 原生全长 288 帧完成（225.26 秒，errors=[]），完整 PNG/MP4 解码通过，12 秒/24fps。突发变暗检查无异常；实际查看第 124/228/269/287 帧，扫描顺序、后门连续余辉和末段无遮挡成立。420 项保护文件仍全部一致；已请求在 Codex 打开预演视频（工具返回 queued）。
- 在完整修正版预演通过后启动 Final_v06_4K：3840×2160、8 时域采样、288 帧。最终 4K 与轻量副本仍待渲染、解码和视觉复核。
- Final_v06_4K 生成过程中实际查看第 0、50、82、96 帧：开场网格关闭，贴面光从引擎盖经侧门到后轮拱，世界空间尾迹显现，未见未激活区域的黑色管线。此为关键帧视觉检查，未宣称最终完整视频已通过。
- 继续实际查看原生 4K 第 124/163/189/228 帧，确认网格从车头依次覆盖前门、后门和后翼子板；第 228 帧（9.5 秒）整车余辉连续，后门没有概念图中的空白。尾迹可见；末段仍在输出，完成后再检查末帧并编码。
- Final_v06_4K 原生 MRQ 完成，3840×2160、288 帧、8 时域采样，耗时 800.36 秒，success=true、errors=[]。实际查看末帧 287，车身完整可见且网格/尾迹已收束；开始全 PNG 解码、异常变暗检查、H.264 编码与成片全解码，尚未把编码结果标记为通过。
- Final_v06_4K 全部 PNG 解码、尺寸/连续帧号检查和 H.264 完整解码通过：288 帧、24fps、12 秒，abrupt_darkening_flags=[]，末帧 mean=0.15605；第 269/287 帧实际查看均无遮挡。主 MP4 SHA256=f879ba2de61769c1c0da9bdf98b480e3da5df1ba017ca8140fa534661541e860，420 个保护文件哈希仍全部一致。正在从已验证主文件生成 1080p 观看副本。
- 1080p 观看副本已从最终 4K 主文件下采样并完整解码（288 帧/12 秒），SHA256=2c1b6ae9c40508717cc8c32333ac817d71fc1f4f3a4438d921e67013b2b7b0ef；已请求在 Codex 打开（queued）。原始帧没有 AI 修图或外部合成；当前为无声版。
- tunnel33_finish 最终保存、先清 LVS 缓存再重载及审计通过：121 个原车辆唯一可见网格、420 个既有文件保护一致，4K/8 时域 MRQ preset 持久化正确，Map Check 0 Error / 0 Warning，dirty_maps/dirty_content 均为空；本轮编辑器任务轮询已注销。原地图/模型均保留，新镜头入口见 art/YU7_TUNNEL_FLOW/README_UE.txt。
- 署名 sidecar 与根 CREDITS.txt 逐字节一致，序列 metadata 和视频 comment 已记录原文。最终应用内可见 Credits 仍待后续交付集成；本轮未做打包运行、新机器验证或声音制作。新增内容保存于本地，本轮未执行 Git 提交/推送。
- 已直接复制五张原生 4K 关键帧至 renders/YU7_TunnelFlow/01_CleanPaint_4K.png 至 05_FadeOut_4K.png；output_manifest.json 收录 58 项工程资产、准备源及最终媒体的尺寸/哈希。git diff --check 通过，仅提示既有 Windows CRLF 将在后续 Git 操作规范化。

## 39. 2026-10-17 — Roof airflow revision (contemporaneous)

- 用户指出流光只有侧面两条，要求空气动力学般越过车顶的流光。检查 tools/yu7_tunnel_geometry.py 确认旧光路仅为两侧肩线/轮拱线和短引擎盖线，并且只允许 CarPaint 命中，未建立越过风挡与车顶的路径。
- 本次增加七条不同高度的纵向上方气流弧线，贯穿引擎盖、前风挡、车顶与尾翼上方，并延伸为高位尾迹。保持既有完整车门 quad、摄影机和行驶时序；采用新增版本化几何和原生材质/MPC 时间控制，无运行时 Python/C++。先检查关键帧，再输出完整修正版观看视频；不覆盖 v06 媒体。
- 第一次 Blender 探查引用了上次调用的局部变量而失败，确认 MCP 每次代码执行不共享局部作用域；改为每次自包含读取。几何生成与导出成功：七条曲线、92,400 三角形，实际源网格上方最小间距 0.15754 m，121 个原对象保留，输出 prepared/YU7_RoofAirflow_v01.blend/.fbx。这是示意气流线，未进行 CFD 仿真。
- roof01_prepare 已创建完整工作地图备份 Studio_YU7_TunnelFlow_BeforeRoof_v06，额外保护 58 项 v06 工程/媒体文件。roof02 正在新增 BP_TunnelRoofAirflow_v01 和原生 Masked 材质；旧五个效果资产、序列和车漆均不修改，视觉结果待渲染。
- roof02 新增资产成功，roof03 三张 1080p 原生 MRQ 帧成功（33.54 秒，errors=[]）。实际查看 1.0/4.0/9.5 秒：开场关闭，上方七条气流绕过风挡、车顶并延伸高位尾迹；9.5 秒顶部仍连续发光且后门 quad 完整。准备保存后重载审计和全长修正版预览，尚未确认连续运动。
- roof04 按 LVS 清缓存流程保存后重载成功：原 121 个可见网格保持、新增屋顶 Blueprint 持久化为 Movable/NoCollision/无投影，七条线 92,400 三角形；原 420 项及额外 58 项 v06 文件哈希全部一致，无 dirty packages。进入 4K 两张关键帧及完整 1080p 修正版输出。
- Roof_Keyframes_v07_4K 两张原生关键帧完成（63.33 秒，errors=[]），实际查看第 228 帧确认顶部气流与整车 quad 同时清楚可见。Previs_v07_1080p 正在输出全长；实际查看其中第 96 帧与单帧渲染的形态一致。指南和 AGENTS 已记录新增 Blueprint 的附着关系，区分其车周稳定气流路径与旧世界空间尾迹。
- Previs_v07_1080p 原生 288 帧渲染完成（138.59 秒，errors=[]），全部 PNG/MP4 解码、尺寸、连续帧号和 12 秒/24fps 检查通过；abrupt_darkening_flags=[]，实际查看末帧 287 无遮挡且气流已消退。视频 SHA256=d330aec74f4a9ad0a233a3cf863b272d6e558d3acd08ff25e2df9e7b9d1acfed，420 项原始保护文件不变。
- 两张原生 4K 对照帧已复制为 RoofAirflow_v07_4K.png、RoofFullBody_v07_4K.png，额外 58 项 v06 文件保护通过；roof_output_manifest_v07.json 记录本轮资产与媒体哈希。当前交付 1080p 全长修正版及 4K 对照帧，没有将旧 v06 4K 视频冒充车顶修正版。已请求 Codex 打开修正版视频（queued）。
- roof07_finish 最终保存后安全重载审计通过，Map Check 0 Error / 0 Warning；420+58 项保护文件仍一致，七条屋顶气流 Blueprint 持久化正确，编辑器任务轮询已注销。本轮 10 项交付清单哈希与最终保存资产完全一致；git diff --check 通过。仍为无声版本，未执行本轮 Git 提交/推送。

## 40. 2026-10-18 — Pulsing, undulating roof airflow (contemporaneous)

- 用户要求顶部线条亮度更明显地脉冲变化，并减少平行静止感，增加类似侧面流光的优雅起伏。v07 恒定底亮度为 0.18×1600，亮段之外仍较亮，且路径几何静止；本轮降低底亮度、错开每条线的脉冲相位，并用原生材质 WPO 添加沿路径传播的缓慢上下/横向波动。
- 继续使用 MPC ShotTime 驱动，保持可逐帧求值，无运行时 Python/C++；新增版本化材质并仅在工作地图覆盖屋顶组件材质，保存 v07 地图备份和原资产。先验证车顶间距与关键帧，再制作全长修正版视频。引擎材质头文件不在旧 Classes/Materials 路径，使用 rg 定位当前安装路径。
- Computer Use 在 Message Log 上发送关闭快捷键后，实际主编辑器一并退出；日志确认正常关闭，先前审计状态没有未保存包。停止使用旧窗口句柄，改从已保存工作地图重启。此时尚未运行材质修改或地图备份任务。恢复后继续局部工作，不重建已有资产。

## 41. 2026-10-19 — Resume roof pulse revision (contemporaneous)

- 回溯补记 10 月 18 日中断前的实际结果：pulse01_prepare 已成功创建 Studio_YU7_TunnelFlow_BeforePulse_v07，另有 71 项既有 TunnelFlow 资产/媒体保护快照。roof_pulse_geometry_v08.json 记录 98,007 个离线空间/时间样本，计入管线半径后的最小车体间距约 8.12 cm；这属于采样验证，不是 CFD。新材质脚本当时尚未执行。
- 用户要求继续。本次先只读检查当前 UE 地图、未保存包和材质状态，再恢复已准备脚本；不重复备份或重建已有网格。当前编辑器仍运行，旧任务轮询已超时，需要从控制台重新启动。
- pulse02_resume_probe 确认工作地图正确、无渲染、无未保存包；pulse03_apply 创建 M_TunnelRoofAirflow_Pulse_v02 成功（161 个原生节点），只覆盖当前地图屋顶组件。底光降低到 0.007，移动脉冲和分线呼吸叠加，横向/纵向 WPO 已启用并扩大组件边界；正在输出 4.0/4.5/9.5 秒原生关键帧，视觉尚待复核。
- Pulse_Keyframes_v08_1080p 三帧原生渲染成功（29.97 秒，errors=[]）；实际查看 4.0/4.5 秒，亮段位置、各线高度和尾部起伏随时间改变，9.5 秒完整前后门网格保留。pulse05_audit 按 LVS 清缓存流程重载后，121 个原网格、420+71 项保护文件和材质实例覆盖/位移开关均通过，Map Check 0 Error / 0 Warning。
- 审计中旧辅助函数 EditorSetViewportRealtime(True) 触发已处理 ensure：不存在可移除的 realtime override；没有崩溃，资产审计完成。该调用只影响编辑器预览刷新，准备移除这项非必要 UI 设置，避免后续审计重复触发。完整 1080p/288 帧预演已提交，连续运动尚待输出检查。
- 已查 UE 5.8 本机 LevelEditorSubsystem.cpp：EditorSetViewportRealtime(True) 实际移除具名 override，未预先添加时会触发 ensure。tools/ue_tunnel_audit.py 已移除该非必要调用，保留用户当前刷新设置；下一次最终审计会验证修改。全片已输出前段，实际查看第 80/124 帧，流线亮峰和波形随时间变化，网格仍按原时序从前向后启动。
- Previs_v08_1080p 原生全长 288 帧完成（157.80 秒，success=true、errors=[]）。实际查看第 269 帧确认车顶气流按时消退、车辆无遮挡；正在进行全部 PNG 解码、连续帧号/突发变暗检查与 H.264 编码，并输出两张原生 4K/8 时域关键帧。
- Previs_v08_1080p 全部 288 张 PNG 和 MP4 完整解码通过，1920×1080、24fps、12 秒，abrupt_darkening_flags=[]，原 420 项保护文件不变。视频 SHA256=dac38efecf6c70796e842b1ac5f3c803639cc0f3c68cb4d62bbfa2b6c7f338b4。实际查看末帧 287 无遮挡，全部气流和网格已收束；已请求 Codex 打开新版观看视频。4K 关键帧与最终保存审计仍在进行。
- Pulse_Keyframes_v08_4K 两张原生 3840×2160/8 时域静帧完成（66.02 秒，success=true、errors=[]）；实际查看 4.0/9.5 秒图确认线条亮峰、弧线起伏与后门连续 quad，复制为 RoofPulse_v08_4K.png、RoofPulseFullBody_v08_4K.png，未做 AI 修图或合成。
- pulse08_finish 最终保存后按 LVS 清缓存流程重载，121 个原车辆唯一可见网格、420+71 项保护文件全部通过，Map Check 0 Error / 0 Warning，无未保存包。移除非必要 realtime setter 后本次审计未再出现相关 ensure。已写本地任务轮询关闭请求。
- pulse_output_manifest_v08.json 记录最终保存地图、新材质、备份、渲染预设和媒体哈希。README/AGENTS 更新了当前材质实例覆盖、位移边界与版本入口。本轮交付 12 秒 1080p 无声预览及两张原生 4K 图，未渲染 v08 全长 4K，未执行 Git 提交/推送；应用内可见 Credits 和打包运行验证仍待最终项目交付。

## 42. 2026-10-19 — Art-direction review (contemporaneous, proposals only)

- 用户询问 art director 视角仍缺少什么。复核 v08 开场、第 163/200/280 帧，并结合前轮已查看的流线/整车网格关键帧和原生时间设计进行审美评估；本轮没有调整场景或材质，也没有宣称通过播放器实时观看完整视频。
- 建议优先改善车身灯光塑形（前挡白色反光块、门板宽高光）、区分顶部主辅流线并加强与风挡/车顶曲率的关系；清理画面下缘显眼黑色条带、降低隧道灯带与效果线的竞争；让网格完成、摄影机减速与主光形成明确峰值，最后给干净车身留出展示时间。无声状态下，风声/轮胎低频/克制电子脉冲可作为后续声音方向。以上均为艺术指导建议，尚未获得实施指令，未标记为完成。

## 43. 2026-10-19 — Detailed art-direction design and session handoff (contemporaneous, not implemented)

- 用户明确要求把上一轮艺术指导意见 1–4 具体设计并写入设计文档与开发记录，实现只在新 session 处理。本轮范围仅为文档，未启动 UE/Blender 修改、制作脚本、渲染、新会话或后台任务。
- 已阅读实际 v08 指南/交付清单、既有 SHOT_DESIGN_v01.txt/CONCEPT_REVIEW_v01.txt、屋顶几何脚本和 v06 摄影机修复脚本。原计划的 docs 目录不存在；改用项目既有 art/YU7_TUNNEL_FLOW/design 目录及 .txt 格式，不重写早期设计或历史记录。
- 新增 art/YU7_TUNNEL_FLOW/design/ART_DIRECTION_v09.txt，记录灯光塑形、两主五辅流线、环境层次、高潮节奏四项细节。包括灯光隔离诊断/尺寸/强度起点、主辅线亮度/线径/净距/波幅、粗黑条带来源诊断、路面反射、帧级 cue、摄影机姿态起点及连续运动验收。所有新参数是待预演调整的设计目标，未当作实测值。
- v09 设计核心：主光头帧 114→204 从车头到车尾，网格以同一车身进度落后 8 帧（帧 122→212）；约帧 222 / 9.25 s 汇聚后肩高光、尾部流光与完整网格，摄影机相对环绕放缓；帧 264→287 保留完整一秒无效果车漆。明确屋顶 11 m UV 与车身 UV 不能直接混用；新曲线和相机需要重新验证净距与全片遮挡。
- 新 session 基于 v08 创建隔离的 ArtDirection_v09 地图、序列及待改资产副本，不修改既有源模型/完整后门 quad/历史资产。计划先灯光和场景诊断、再流线与接力、最后连续预演和原生输出；文档提供读取顺序、版本化路径、验收帧、保护规则与可直接复制的新 session 指令。这些 v09 工程路径尚未创建。
- 用户表示之后会提供路上见过且喜欢的车漆示意图。已单列后续材质接口：现阶段沿用矿物青，只做灯光设计；等待真实参考后分别分析颜色、角度变化、颗粒、清漆与拍摄条件，在固定中性照明下比较独立实例。不提前猜测或实装新车漆，不覆盖矿物青 baseline。声音第 5 项不在本次范围。
- 同步在 AGENTS.md 和 art/YU7_TUNNEL_FLOW/README_UE.txt 增加交接入口与 session 边界；当前完成版本仍然是 v08，设计文档完成不代表 v09 已实现或验收。
- 文档复核修正了帧区间记法：帧号范围包含首尾，秒数区间前闭后开，避免 24fps cue 交接歧义。10 个既有交接文件引用均存在；pulse_output_manifest_v08.json 的 13 项资产/媒体 SHA256 全部一致。git diff --check 通过（仅既有 CRLF 规范化提示）。这些检查只验证文档与基线保护，不验证尚未实施的 v09 视觉。

## 44. 2026-10-19 — Publish tunnel/roof revisions and art-direction handoff to GitHub (contemporaneous)

- 用户明确要求将现有更新同步 GitHub。当前分支 main、origin=https://github.com/VegaBai/vehicle-visualization.git；fetch 后本地 HEAD 与 origin/main 均为 9dd92d8，ahead/behind 为 0/0。沿用该分支保存当前成果，不启动 v09 实现。
- 提交范围包含独立隧道工程、v06 原生 4K 成片、v07/v08 车顶气流与脉冲成果、精选/诊断静帧、准备资产、工具、验证报告、署名与 v09 设计交接文档。初步盘点 284 个新增文件约 379.15 MB，另有 5 个已修改文件；模型、UE 资产和媒体沿用 Git LFS，完整可重渲帧目录按现有 gitignore 留在本地。
- 提交前文件检查：原 420 项保护文件、额外 71 项 TunnelFlow 保护文件、v08 当前 13 项交付清单哈希全部一致，两处 CREDITS 与根文件逐字节一致。172 个候选文本文件的常见凭据签名扫描无匹配（不等同完整安全审计）。此次只做版本管理与文件完整性检查，不重跑已通过的 UE 渲染或声称完成打包验证。
- 下一步暂存、检查 LFS/普通 Git 对象和提交差异，再推送；远端完成状态待实际命令结果。
- 暂存完成，共 289 个文件，其中 116 个二进制/媒体文件为 LFS 指针；普通 Git 对象最大 129,251 bytes，没有把大型资产直接写入普通 Git。
- 全量暂存空白检查仅报告 11 个 FFmpeg 原始 encode/decode 日志的行末空白及末尾空行。为保留诊断输出，未改写这些历史日志；对其余全部暂存文件执行 git diff --cached --check 通过。这是原始日志格式问题，不是代码或设计文档错误。
- 主成果提交 aefdf8d7f09505df418091ae3cfb146d1558a586（Add YU7 tunnel cinematic and pulsing roof airflow）已成功推送 origin/main。Git LFS fsck OK，112 个新增去重对象约 348 MB 上传完成，对应 116 个新增 LFS 文件；普通 Git 提交共 289 个文件。
- git ls-remote 核实远端 main 与本地完整 SHA 一致，git lfs push --dry-run 无待上传对象，主成果推送后工作区干净。将本条实际发布结果通过随后纯开发记录提交同步，保留主成果提交历史。v09 仍仅完成设计，具体实现等待新 session；新的车漆材质仍等待用户参考图。

## 45. 2026-10-19 — Implement isolated art-direction v09 (contemporaneous)

- 用户在新 session 要求根据最新设计文档和开发记录继续；本轮开始实施 ART_DIRECTION_v09.txt 的四项范围。已读第 41–44 节、v08 最终审计与工具；Git 工作区起始干净。保持现有矿物青与全部历史资产/媒体，新的车漆等待参考，声音仍不在范围内。
- 当前未发现运行中的 UnrealEditor/Blender。准备从已保存 v08 地图启动编辑器，先只读检查无活动渲染和未保存包，再采集保护快照、创建隔离地图/序列/待修改资产。实现使用原生 Blueprint、Sequencer 和材质节点，Python 只作编辑器准备及离线检查。
- 已新增 tools/ue_ad_v09_probe.py；尚未修改 UE 内容，也未验证 v09 视觉。先定位反光和粗黑条带，再推进流线、接力、摄影机及连续原生输出。
- 环境诊断修正：受限命令行 Get-Process 未列出交互桌面的 UE/Blender；Start-Process 返回 PID 后未形成可见新编辑器或新日志，不能以该结果断言应用未运行。Computer Use 的窗口清单实际发现原 UE 与 Blender 会话。转为核对既有 UE 窗口并恢复旧任务接口；此前未运行内容修改脚本。
- ad09_01_probe 成功：当前为已保存 v08 工作地图、无 MRQ、无 dirty packages、v09 目录不存在。已恢复既有本地编辑器 job runner；截图坐标需使用 screenshotId，普通窗口坐标没有正确聚焦输入框，未触发内容修改。
- tools/yu7_ad_v09_protect.py 创建 510 项源文件/UE 资产/既有媒体保护快照；原 420 项、额外 71 项及 v08 manifest 检查全部一致。新增 v09 prepare/render 工具采用版本化资产断言，正在创建主工作副本和 CleanBaseline/NoFront/NoSide/NoRoof/NoCeiling/NoRibs 原生诊断地图与序列；不根据名称预断反光/黑带根因。
- ad09_02_prepare 成功创建 v09 主地图/序列、11 个待改资产副本和六组诊断地图/序列，所有序列绑定在副本地图解析到有效对象。首轮 Diagnosis_r01 MRQ 技术成功（12 帧/31.95 秒），但实际对照图全部相同且效果仍出现，因此诊断无效，不用于根因结论。
- 诊断流程修正：PIE executor 应先加载所渲染的地图，不能依赖同一队列各 job.map 切换；同时显式 modify Actor/组件后保存可见性更改。新增 ue_ad_v09_diagnostics.py 在每组结束后安全清 LVS 缓存并切换地图，再独立渲染。r01 图保留为失败证据。
- Blender 已创建独立 YU7_RoofAirflow_AD_v09.blend/.fbx，七条线拆分成独立网格便于核对实际导入近侧；主线直径 5.2 mm、辅线 3 mm，局部净距随原车表面变化。原 121 个对象未改动。96 Hz / 3,010,483 个最近三角形距离采样（转折处 2 cm）计入管半径后最小净距 13.46 cm，最大合成位移 17.92 cm；原生材质尚未接入或渲染验证，不是连续碰撞保证/CFD。
- r02 六组同机位原生对照（24/228 帧）实际复核：RoofFill 关闭使前挡白块消失；SideFill 关闭去除门板宽横高光。NoRibs 未消除粗黑条带，另建 NoLane 对照，r03 确认隐藏 Tunnel_Lane 的两实例后黑带消失。起始探查显示这两实例当前 visible=True、hidden_in_game=False，不能沿用旧记录的“已隐藏”结论。修正仅在新 BP 副本清除可选标线实例，保持道路与隧道。
- ad09_05_effects 成功导入七个独立线网格并建立原生材质与 BP 副本。UE 实际组件包围盒证实 lane 5/6 在摄影机侧 world +Y（中心约 +50.82/+70.28 cm）；不把 lane 0 误当近侧。既有 grid/surface UV 实际为 (2.5-x)/5，而非近似包围盒 4.98 m；屋顶采用精确等价 2.2*U-0.2，主光头帧114→204、网格122→212、全部效果264前消退。材质接入成功，动态外观尚未验收。
- 开始灯位与镜头修订：复制环境材质/BP，填充灯先降至 65–70%，缩窄并移开 RoofFill/SideFill，新增长条塑形主光及弱远侧轮廓。灯带降至 65%，路面粗糙度变为低频纵向变化0.34–0.44；不修改车漆或玻璃。当前已保存顶灯的实际 rotation 为 roll=-90/pitch=0（旧脚本 positional Rotator 参数顺序问题）；新副本采用显式 pitch=-90 朝下，待原生对照验证。
- ad09_07_scene 在创建路面粗糙度节点时因 UE 的 const_b 只能通过 editor property 访问而中止；两份灯带材质的0.65缩放已保存，灯光/环境 BP 尚未调整。r04 clean render 在该错误后被误提交，只代表部分状态，不作灯光验收。已修正访问方式并新增精确续作脚本，跳过已保存灯带缩放，避免重复乘0.65；正式对照升为 r05。
- ad09_09 续作因 r04 仍在渲染而被开头断言拦截，未修改任何内容；等待 r04 完成后 ad09_10 精确续作成功。新 BP 标线实例数为0，材质、灯位与原生长条主光已保存。r05 现在输出同 v08 摄影机的24/228/276帧干净车身对照；新版摄影机尚未应用，便于判断真实灯光变化。
- r05 三张1080p/8时域干净车身对照成功（29.18秒），实际查看24/228/276帧：黑条带完全消失、门板高光变窄，但车顶/引擎盖和路面出现过强白区，灯光视觉未通过。按图像降低新窄光源能量、前移塑形灯，顶灯降至6000lm/specular0.2，RoofFill降至8000lm，保持相机曝光/漆面/玻璃不变；此为基于实测图的调整，超出首轮60–80%仅为设计起点的区间。
- r06 三张1080p/8时域干净车身对照完成（29.49秒），实际查看24/228/276帧：路面黑带消失，主体矿物青暗面恢复，肩线高光更窄，白反光集中为局部窄带而非原前挡整块白区；轮胎与接地仍可读。采用该灯光方案进入运动预演，最终仍需动态确认。
- ad09_14_sequence 应用新相机：40mm固定，35→112°同侧环绕，9.0–9.5s放缓；使用单调Hermite起点曲线逐帧烘焙为原生关键帧，避免每段零速度顿挫。保持原15m/s与轮转轨道，塑形主光从前向后移动并在9.15–9.3s提升1.25倍；扫描真实光随同车身u。未改变固定曝光。当前开始保存/安全重载及实际环境几何净距检查。
- 从新版 BP 导出426个实际可见实例的有向包围盒，按96Hz/1153个时刻检查原生线性相机关键帧：最小净距69.23cm（11.15625s，Tunnel_Ribs instance204），中心视线无构件交叉，方位单调；达到50cm目标，仍需全片视觉确认。
- ad09_15 重载后资产/绑定检查进行到署名断言时中止：UE duplicate_asset 没有保留序列 Attribution metadata。未将该审计标为通过；新增专用脚本从根CREDITS原文恢复新序列署名，并采样MPC与15m/s原生位移后重试审计。原文件/旧序列不修改。
- ad09_16 恢复新序列署名成功；15个关键时刻实测原生MPC ShotTime与车辆世界X均符合帧号/24秒及15m/s。ad09_17 按LVS清缓存流程保存后重载审计通过：121个唯一可见原车网格、三套完整quad共99,916三角形、七条新屋顶网格共92,400三角形、正确父级/NoCollision/Movable/WPO速度输出和25cm上限，世界尾迹未附着。所有新序列绑定指向v09地图，510项保护哈希全一致，Map Check 0 Error/0 Warning，dirty packages为空。
- 已提交 Previs_r07_720p 全长288帧/24fps/8时域原生预演。当前审计仅确认持久化与采样，不替代随后运动细线、接力、高潮和末帧视觉验收。
- Previs_r07_720p 原生288帧完成（77.29秒，success=true、errors=[]）；全部PNG与12秒/24fps MP4解码通过，510项保护文件一致。实际逐组查看覆盖0–287的12张逐帧接触表及84/216段细节：无黑条遮挡，网格仅从前向后建立一次，前后门完整，264–287效果全灭。两条近侧白芯主线与青色细辅线可分；风挡附近存在透视交会，未见连续密集编织。此为逐帧图像和视频解码检查，未声称播放器实时观看；下一步1080p连续细线复核及原生4K关键帧。
- 新增 README_AD_v09.txt 记录实际资产入口、材质/灯光/镜头参数、失败诊断和安全复用边界；当前明确标记1080p/4K输出尚待完成。新增 yu7_ad_v09_finish.py 用于最终媒体、原420/71/510项保护、精确署名和原生精选帧哈希检查，尚未执行。
- Previs_r08_1080p 原生全长288帧/8时域完成（156.67秒，success=true、errors=[]）。实际查看全部12张逐帧接触表、96/122全分辨率图及接力细节：未见整帧遮挡、重复扫描、主体出画或末段突暗；辅线随相位降低亮度但保留连续路径，高潮后门完整，末24帧无效果。开始7张原生4K关键帧验证；MP4编码/完整解码仍在进行。
- 1080p PNG与MP4全解码通过：1920×1080、24fps、288帧、12秒，abrupt_darkening_flags=[]，510项保护不变，视频SHA256=e7ab35621d211f0d256be5ba4144f3d122ced901e17721c98255382f0232ae3e。已请求在Codex打开本轮1080p预览；当前继续原生4K关键帧，不将1080p描述为最终4K交付。
- 修正新屋顶准备脚本的报告文字：几何创建时的body_u采用4.98m近似包围盒，实际原生图已使用与旧grid一致的5m域。现在脚本报告写为(2.5-x)/5=2.2*roof_U-0.2，并在现有roof_geometry.json附加后续更正；未重跑脚本、未改网格或材质。
- Keyframes_r09_4K 七张3840×2160/8时域原生静帧完成（195.56秒，success=true、errors=[]）。实际查看24/96/122/163/222/269/287：白芯与细辅线、单次局部网格接力、完整后门/镜壳和结尾清车均可辨，无新增黑条遮挡；采用当前场景开始Final_r10_4K全长288帧原生输出。
- AGENTS.md/README_UE.txt 已改为v09实际工程入口，明确全长4K仍在渲染；原设计文件只追加实施追记，不改写设计session的历史限制。README_AD_v09保留当前矿物青/无声范围和应用Credits、打包验证尚待最终项目交付的边界。
- 全长Final_r10_4K按完成的24帧组生成接触表并逐组复核，当前已查看0–143：开场无效果、描形渐入、114附近收敛、122后单次车鼻网格启动均与预演一致；渲染仍在进行，未提前记录最终完成。review_sheets支持只处理已完整写出的帧组，原生PNG不变。
- Final_r10_4K 原生3840×2160/24fps/288帧/8时域全长渲染完成（650.00秒，success=true、errors=[]）。已逐组复核0–239帧，当前补查末段、PNG完整解码与视频编码，并提交最终保存后安全重载审计；此时MP4尚未完成。
- 已补查Final_r10_4K末两组接触表，0–287全部帧现已覆盖；240后仅渐暗，264–287无网格/屋顶/世界尾迹，269与287无遮挡。visual_review.json明确记录图像/接触表检查依据及未声称实时播放器观看、人类验收。ad09_22最终安全保存重载成功，Map Check实测0 Error/0 Warning，121原车网格、完整quad、新绑定、510项保护和空dirty列表再次通过。
- 最终4K全部PNG与MP4完整解码通过：3840×2160、24fps、288帧、12秒、无声，abrupt_darkening_flags=[]，视频SHA256=bdfa5ef8845ab8ff80e4b1868146ff56fa855387fcfa29a65fdc4dcf76806264。yu7_ad_v09_finish.py成功生成output_manifest.json：3份视频、7张从最终序列原样复制的4K精选帧、7张4K预检帧、87项新资产/源文件哈希；视频容器署名与sidecar均核对原文。510/420/71项历史快照及v08清单13项全部一致。
- AGENTS/README已更新为完成的v09入口和实际4K成果，未改原设计历史。已发送本地编辑器轮询停止请求；场景保持保存的v09首帧视角。仍保留矿物青并等待新车漆参考，声音不在范围内；应用内可见Credits、打包/新机器验证留待最终项目交付。本轮未执行Git提交或推送。
- 最后文本差异检查git diff --check通过（仅仓库既有CRLF规范化提示）；23个本轮Python工具语法解析通过。已请求Codex打开最终4K MP4，工具返回queued。全部实际输出、保护清单与剩余项目交付项已写入README_AD_v09和报告。

## 46. 2026-10-19 — Smooth roof airflow over body details (contemporaneous)

- 用户附图指出车顶流线局部有棱，要求曲线无视车身小棱角并保持平滑。将“ 五十 ”按上下文理解为“无视”；本轮处理曲线几何，保持既有矿物青、镜头、灯光、接力节奏及 WPO。
- 只读检查确认 v09 的逐点车身上包络抬升、随后 max(original, average) 平滑保留了雷达/车顶凸起造成的短折角：lane 2/3 的最大高度二阶差分约 40.80/37.57 m^-1，其他线约 1.53–2.07 m^-1。先前全片接触表未识别该局部问题，不能用原视觉记录否定用户反馈。
- 决定创建独立 RoofSmooth_v10 地图、序列、Blueprint 和七个线网格，原 v09 及其交付媒体保留。采用 0.35 m 宽度的平滑高度轮廓及整体 2.5 cm 抬升，取消逐点贴合局部凸起；这只是制作参数，是否通过需重新检查全时段净距和原生画面。Python 仅作准备/离线验证，运行保持原生 Blueprint/材质/Sequencer。
- 已建立 658 项历史文件保护快照（包括 v09 资产、源码、交付和报告），并另存 YU7_RoofAirflow_Smooth_v10.blend/.fbx。统一按原始 1 cm 差分计算，lane 2/3 峰值为 62.24/75.06 m^-1（前一条探查使用不同差分步长），平滑后七条线均低于 0.49 m^-1；报告明确记录算法/尺度，不混用两种数值。
- 首次净距脚本因 Blender exec 环境没有 __file__ 中止，改为明确脚本路径后完成。3,010,483 次 / 96 Hz 采样计入管径，最小动态净距 13.684965 cm（lane 3，4.3125 s），静态最小 16.3162 cm；原 WPO 最大位移仍为 17.9223 cm。这不是连续碰撞保证或 CFD。编辑器只读 probe 成功，无活动渲染或未保存包，v10 尚不存在，准备导入隔离副本。
- smooth10_02_prepare / 03_audit 成功：隔离 v10 地图、序列、BP 与七个新网格保存并安全重载，绑定全指向新地图，658 项历史文件一致，原车 121 网格与完整 99,916 三角形 quad 保留。Keyframes_r01_4K 原生三帧完成（121.33 秒、无错误）；实际查看 96/122/163 全帧及同机位原生像素局部对照，原先两处明显短折角消失，转为连续长弧。RoofCurve_Before_After.png 为检查裁剪对照，原生 PNG 未修改。开始全长 1080p 连续复核。
- Previs_r02_1080p 原生全长 288 帧完成（155.18 秒、success=true、errors=[]）。实际查看覆盖 0–287 的 12 张逐帧接触表及 84/156/216 屋顶细节组：原局部折角未再现，波动保持连续，后门网格完整、末 24 帧效果已消失。尚未声称实时播放器观看。开始 Final_r03_4K 原生全长输出，同时对 1080p 全部 PNG/MP4 做解码与署名检查。
- 1080p 全部 PNG 和 MP4 解码通过，1920×1080 / 24 fps / 288 帧 / 12 秒；658 项历史保护文件一致，视频 SHA256=fa5dfbae4aedc94c9d66c0aa46a90d8a6d863b135f81f1a7f3b47f3a1be7e1b7。全长 4K 渲染中，当前已检查其 0–119 接触表和 84–104 屋顶细节，折角修正与关键帧一致；尚未标记 4K 完成。
- Final_r03_4K 原生 3840×2160 / 24 fps / 288 帧 / 8 时域输出完成（679.43 秒，success=true、errors=[]）。已实际检查覆盖 0–287 的 12 张接触表及 84/156/216 屋顶细节组，折角修正持续成立，末 24 帧无效果；完整编码/解码尚在进行。smooth10_07_final_audit 保存并清 LVS 缓存重载通过，Map Check 实测 0 Error / 0 Warning，无 dirty packages，658 项保护一致。
- 最终编码与完整解码通过：Final_r03_4K_12s.mp4 为原生 3840×2160 / 24 fps / 288 帧 / 12 秒无声成片，SHA256=036db47cf4b741acfe803d25854a67d6019ccebd9b91d8d87db5b1d56338f4a4。finish 工具核实两份视频、七张原样复制的精选 4K 帧、三张原生 4K 预检帧和 17 项新资产/源文件；原文署名在视频容器与 CREDITS sidecar 中一致。658/510/420/71 项保护清单及 v08 13 项 manifest 全部一致。README_SMOOTH_v10、README_UE 和 AGENTS 已更新最新完成入口；已发送编辑器轮询停止请求。本轮未提交或推送 Git，应用 Credits UI 与打包/新机器验证仍属最终项目交付工作。

## 2026-10-20 · README 最终主视觉与五秒视频展示（当次记录）

- 用户要求将最终效果图加入仓库 README、附上 5 秒运镜视频链接并推送。选用与该五秒镜头配套的矿物青主视觉 renders/YU7_MineralHero/YU7_MineralTeal_4K.png 与 YU7_MineralTeal_5s_4K.mp4；未将后续 12 秒隧道镜头混称为五秒视频。
- README.md 顶部新增作品展示区：直接嵌入原生 3840×2160 PNG，附 MP4 查看/下载链接及 24 fps / 120 帧 / 无声说明。使用 GitHub media 地址读取既有 LFS 媒体，不重复生成、修改或上传图像/视频。
- 已实际查看主视觉；本机两份媒体 SHA256 均与 reports/hero/delivery_validation.json 一致。远端两个媒体 URL 均返回 HTTP 200，长度分别为 8,313,784 / 4,980,026 bytes；图片 Content-Type 为 image/png，视频为 application/octet-stream，链接可能触发浏览器下载，不声称 README 内嵌播放器。
- git fetch 后 HEAD 与 origin/main 为 0 ahead / 0 behind，初始暂存区为空。工作区已存在 v09/v10 及其他未提交制作内容，本次只暂存 README 与本条开发记录；既有 DEV_HISTORY 增补保留在工作区，不随此次文档更新提交。
- 默认 python 命令解析到不可访问的 WindowsApps 别名；本次无 Python 运行需求，改用 PowerShell 与 Git 原生命令单独构建日志暂存内容，避免触碰现有未提交历史。下一步校验限定提交差异并推送；本次不重做 UE 渲染或打包验收。

- 展示提交 f397d0f7bff82d9804b73174f3b751f11cce478c 已成功推送 main，git ls-remote 核实远端 SHA 与本地一致。GitHub README HTML 接口实际返回新增 img 元素及 MP4 超链接，两个媒体地址已通过 HTTP 200 检查；限定暂存差异的 git diff --check 通过。其余本地修改/新增文件保持未提交，DEV_HISTORY 原先的 50 行制作记录仍留在工作区。本条实际验证结果单独同步为日志提交。

## 2026-10-21 · 发布剩余 v09 / v10 制作内容（当次记录）

- 用户明确要求将剩余未提交的 v09、v10 内容提交并推送远端。已核对 AGENTS、README_AD_v09、README_SMOOTH_v10、最新制作记录及两份 output_manifest；本次为版本管理发布，不重跑一次性创建脚本，不修改 UE 资产或重新渲染。
- fetch 后本地 HEAD 与 origin/main 均为 56ec309，ahead/behind 为 0/0，暂存区为空。待发布为 401 个新增文件（约 435.05 MiB）和 6 个已有文件修改，范围包括隔离地图/Blueprint/材质/序列、Blender/FBX、4K/预览视频、精选与诊断静帧、工具、报告、指南和此前保留的制作历史。
- 既有 .gitignore 修改准确排除了 v09/v10 的完整 Previs/Final 原始帧目录，保留 MP4、精选/预检静帧及检查接触表。ue_jobs/request.json 是 v10 收尾 stop=true 状态，随该轮制作记录提交；不执行该请求或启动编辑器。
- 下一步核对交付/历史保护哈希、署名、暂存路径、LFS 与普通 Git 对象，再提交上传。当前未标记远端完成，也不把历史报告等同本次重新进行 UE/打包验收。

- 首轮交付清单检查：v09 的104项、v10 的29项媒体/精选帧/预检帧/资产哈希全部一致；两版 CREDITS 与根文件字节哈希一致。138 个候选文本文件的常见凭据签名扫描无匹配，87 个 JSON 解析成功；该扫描不等同完整安全审计。
- 首次历史保护核验命令错误地将数组的 PowerShell 成员枚举当作 assets 字段，出现空路径错误后仍输出零差异，该轮保护结论无效，未据此发布。已改为明确区分数组/对象、强制每条 path/sha256 非空并启用失败即停；重试实际逐项验证658、510、420、71项历史保护及v08清单13项，全部哈希一致。
- 原始帧忽略规则抽查通过，远端同步起点正常。接下来暂存并核查 LFS、普通 blob 大小与空白差异；保留历史原始诊断日志，不为格式检查重写其内容。

- 暂存检查完成：407 个文件，268 个文件为 LFS 指针，逻辑总量约433.31 MiB；普通 Git 对象最大479,097 bytes。暂存路径中无 Unreal缓存、本地依赖或完整原始帧目录。
- 完整 git diff --cached --check 仅报告10份历史 FFmpeg encode/decode 日志的空白格式；保留这些原始诊断记录，不为消除提示改写日志。排除 *.log 后的全部暂存差异检查通过，无其他空白错误。
- 本次文件完整性与版本管理检查已通过，继续创建制作成果提交、运行 LFS fsck 并推送。仍以真实推送及远端 SHA 核验结果判断完成。

- 制作成果提交 a7d5fcf336123dbdbc64a970538a8c47e436b976（Add v09 art direction and v10 smooth roof airflow deliveries）已成功推送 origin/main；共407个文件，268个LFS文件。git lfs fsck 返回 OK，推送完成后 git lfs push --dry-run 无待上传对象。
- git ls-remote 核实远端 main 与本地完整 SHA 一致。两个最终4K视频的公开媒体地址均返回HTTP 200，远端长度与本地一致：v09为19,016,964 bytes、v10为18,945,677 bytes。此前 README 主视觉与五秒链接保留。
- 成果推送后 git status --porcelain 为空，剩余制作内容均已提交。原始完整帧序列依旧仅保留本地且未删除；本次未改 UE 资产、媒体像素或运行时功能。将本条真实发布/核验结果通过随后纯日志提交同步，不重写成果提交历史。

## 2026-10-21 · 视频前段漆面 / 车衣展示 v11（当次记录）

- 用户要求在视频前段切换金属、珠光、哑光、亮光及灰蓝/灰色陶瓷镀膜质感，并提供灰蓝亮面参考图。依据最新完成的 v10 隧道视频继续，创建独立 FinishShowcase_v11 地图、序列和材质；历史 v10/v09 与源模型均保留。
- 已读取实际 v10 交付清单、README、当前历史与车漆原生节点实现。当前编辑器未运行，工作区初始干净。先保护历史文件并保存用户参考图，再探查序列/材质 API。运行时继续使用 Blueprint/原生 Sequencer/材质节点，Python 仅准备和验证。
- 建议延长至约18秒以留出漆面停留时间，已发可选时长问题；未获答复前先做不依赖时长的准备。视觉方向为低饱和灰蓝亮面、冷银蓝金属、珍珠白、石墨哑光、灰色陶瓷亮面，最终回到矿物青衔接原效果；参数与实际画面待验证。
- 已建立708项历史保护快照，参考图保存到 art/YU7_TUNNEL_FLOW/references/finish_v11。沙箱普通启动未见有效进程，获自动审批后启动已安装UE；启动完成，未发现阻塞窗口。首次只读probe因不存在get_channel_name方法失败，改为对象get_name，不涉及资产改动。可选时长暂未回复，按约18秒继续。
- finish11_03复制序列后，在加载新地图时UE触发World Memory Leaks检查退出。日志明确新地图的standalone World未被回收；检查磁盘仅有新序列，地图/材质尚未保存。错误原因与既有LVS缓存崩溃不同；保留失败日志。定向恢复改用已验证save_map另存当前v10，再清LVS缓存加载，不重复创建已保存序列。
- 定向恢复已成功另存并加载独立v11地图，MPC创建成功。新车漆节点图在Noise位置输入连接处中止（接口引脚名与预期不符），当前仅新材质未完成；探查实际引脚后只重建本轮未完成材质，不碰历史材质/地图。
- Noise实际输入为World Position（输入数据仍使用网格UV构成的局部稳定坐标）；修正后v11材质、MPC、9个可见漆面材质槽和独立地图已保存。玻璃/灯罩/轮胎未换材质。初始五种方案与原矿物青实参记录在palette.json，尚待实际渲染。时间轴采用首6秒七分之一速，6–8秒平滑加速，8秒后对应原2秒并保持原速，全片18秒。
- finish11_07/08原生序列与保存重载审计通过：432帧/24fps，五种新漆面及回归矿物青在六个原生MPC采样点均符合参数，车辆/轮组/镜头/灯光/ShotTime统一重定时。121原车唯一可见网格、99,916三角形全车quad、v10七条曲线和独立世界尾迹保持；708项历史SHA256全部一致。开始9张1080p关键帧，尚未视觉验收。
- 用户明确选择约18秒。首轮MRQ在9个预设保存后、状态文件和输出帧生成前出现Python插件访问异常，未产生有效关键帧；具体根因尚未确认，不视为材质视觉失败。保留日志及预设，重启直接加载已保存v11地图，使用新r02输出名重试，避免覆盖。
- 重启直接加载v11后，Keyframes_r02_1080p九帧MRQ成功（54.86秒，errors=[]）。实际查看12/42/72/102/138/180/310/366/431：五种漆面有明显颜色/高光差异，哑光宽反射、陶瓷亮面清晰高光成立；矿物青回归，原流线/完整后门quad与结尾清车保留。细颗粒在整车中景不作为独立可辨卖点，参数化珠光为艺术外观而非测量光谱。进入18秒1080p全长预演。
- 已查看预演0–143帧接触表：车身各面同步切换，六帧过渡没有整帧白闪或只改部分面板；当前仍在渲染余下帧。新增独立双语漆面标签编码工具，计划同时保留纯原生无标签版；标签属于离线剪辑层，不是UE运行时依赖。README_FINISH_v11和AGENTS明确本轮入口与尚在进行的状态。
- Previs_r03_1080p完整432帧MRQ成功（229.96秒，success=true、errors=[]），已查看覆盖0–431的18张接触表；五种切换/6.5秒回归矿物青/连续加速/完整后门quad/末24帧无效果均通过图像检查。96Hz离线重定时函数严格单调，速度比例从1/7平滑至1，18秒映射原12秒。未声称实时播放器观看。开始Final_r04_4K原生全长，同时编码预演。
- 带标签1080p预演已完成编码与432帧/18秒完整解码；工具仅在最后控制台打印中文报告时因cp1252编码报错，视频和UTF-8验证报告此前均成功保存。已将打印改为ASCII转义，不重跑或覆盖已完成媒体；字体日志确认微软雅黑与Arial正确加载。
- 1080p无文字版所有原生PNG与MP4完整解码通过（1920×1080、24fps、432帧、18秒，708历史哈希不变），SHA256=915d0e303ccc4768161c821f9a452c193fa6a2e87641ca74c22e1342fe882873。标注版完整解码通过，SHA256=23e7ca266ec4de50022aaf371e2d3e3caa8edf82ed4271885ada83823aee176d；实际查看0.6秒编码帧，中文/英文位置与字体正常，无车身遮挡。已请求Codex打开预演，返回queued。4K全长仍在渲染。
- Final_r04_4K全长输出进行中；已查看0–71逐帧接触表及12/42/72原生关键帧，灰蓝/金属蓝/珠光白整车同步切换成立。16个本轮Python工具语法解析通过。当前不将未完成的4K列为已交付。
- 4K接触表已实际覆盖0–191，五种漆面和回归矿物青的6张原生关键帧均已查看；六格对照图已生成并请求打开。6.5秒材质回归、6–8秒加速衔接未见面板不同步/整帧闪变；后半段渲染尚在进行。
- Final_r04_4K逐帧接触表现已覆盖0–359，并查看310流线/网格交接原生帧；屋顶线平滑连续，后门网格完整。正在等待最后72帧和MRQ完成信号，尚未启动最终编码。
- Final_r04_4K原生3840×2160/24fps/432帧/8时域全长MRQ完成（1469.00秒，success=true、errors=[]）。实际查看18张接触表覆盖0–431及9张关键帧；五种切换、矿物青回归、流线/全后门网格、末24帧干净收尾均通过图像检查。启动无文字/双语标注两版编码并提交finish11_13最终保存/清LVS缓存重载审计。渲染日志有Lumen自动将ScreenProbeGather DownsampleFactor从4增为8的纹理尺寸限制提示，不声称渲染日志零警告；原生输出分辨率仍为4K。
- finish11_13最终安全保存/清LVS缓存重载成功：121原车网格、9个漆面槽、全车quad、原v10曲线、六个原生MPC采样值及新地图绑定通过，708项历史保护哈希一致，dirty列表为空。日志Map Check实测0 Error/0 Warning，摘录保存至final_mapcheck.log。已发送本地编辑器任务轮询停止请求，保留保存的v11首帧场景。最终视频编码尚在进行。
- 最终4K无文字版全部PNG与MP4完整解码通过（3840×2160、24fps、432帧、18秒），SHA256=b65b13e0a82ad1fdf947f47b374a7ec01eefa06c0076759340017b342c05f3be；标注版完整解码通过，SHA256=e779198e11859db380da0a579f6988bae1b4dccf1bd5a35bc7046bd6ba6bcbb8。实际查看从最终标注MP4解码的五种名称及退出帧，均正常。
- yu7_finish_v11_finish.py完成最终manifest：4份视频、9张原样复制的原生4K精选帧、24项本轮UE资产全部记录哈希，视频容器及sidecar署名逐字核实，708项历史保护再次一致。README_FINISH_v11和AGENTS已更新实际完成状态。原生完整帧保留本地并被忽略；未执行Git提交/推送。应用内可见Credits与打包/新机器验证仍为最终项目交付项，本轮未将其标记完成。
- 最后受控文本差异检查git diff --check通过（仅既有CRLF规范化提示）；已请求Codex打开默认4K标注版，返回queued。实际媒体/检查依据/局限均记录在交付清单与指南中。
- 收尾读取停止请求的结果文件时发现无该文件；随后核对ue_editor_jobs.py，stop分支直接注销回调并返回，本来就不生成结果JSON。仅记录停止请求已发送，不把缺少JSON当作任务失败或伪造停止回执。

## 2026-10-21 · README 展示与 v11 发布（当次记录）

- 用户明确要求将18秒视频和漆面对照图更新到README，并提交推送v11制作内容。README新增顶部v11展示区，主链接为带名称4K版，同时提供无文字4K与1080p预览，并嵌入六格对照图；原5秒主视觉展示保留。同步最新地图/序列入口、目录和v11指南链接。
- 本轮只更新文档并发布既有制作成果，不重跑UE创建脚本或重渲。当前main上的待提交修改/新增均为v11相关；下一步核对交付清单、历史保护、署名、暂存范围和LFS，再提交推送。尚未标记远端完成。
- git fetch后本地HEAD与origin/main均为dcb67cd，0 ahead / 0 behind，初始暂存区为空。交付manifest的37项（4视频/9精选帧/24UE资产）SHA256全部一致；708项历史保护哈希和原文署名sidecar一致。164项新制作文件约174.7MiB，64项候选文本常见凭据签名无匹配，33个JSON与16个Python工具解析通过；本轮只做发布完整性检查，不冒称重新UE运行或打包验收。完整Previs/Final原始帧忽略规则抽查通过。
- 暂存范围核对为170文件，其中100项LFS指针，逻辑总量约174.8MiB；最大普通Git对象338,911 bytes。无原始完整帧序列、UE缓存或本地依赖混入。首轮git diff --cached --check发现10份原始日志、api_probe.txt原生文档转储及3个脚本EOF空行；仅移除3处脚本多余空行，保留诊断证据，不改变运行逻辑。下一步复核排除原始诊断后的文本差异、提交与LFS上传。

- 排除10份原始日志及api_probe.txt诊断转储后的全部暂存文本差异检查通过。制作成果提交f1477fb5fce1a9a2bee54e1353223738485fd077（Publish v11 finish showcase and update README with 18-second video）已推送origin/main；170个文件，100个LFS文件、约182MB上传完成。git lfs fsck返回OK，上传后git lfs push --dry-run无待上传对象。
- git ls-remote核实远端main与制作成果提交一致。GitHub README HTML实际包含新对照图和三份视频链接，原5秒链接仍在。三份视频及对照图均HTTP 200，远端长度与本地一致（26,351,735 / 26,290,744 / 8,471,349 / 453,696 bytes）。MP4响应为application/octet-stream，链接可能下载；未声称README内嵌播放已验证。证据写入reports/finish_v11/publication_remote_verification.json。
- 成果推送后的工作区曾核实为空；随后只追加本条真实发布记录及远端检查报告，将以纯记录提交同步，不重写制作成果提交。原始逐帧序列继续留在本地且未删除；本轮未重渲或修改UE资产。

## 2026-10-27 · 鬼灭之刃痛车选图（当次记录）

- 用户提出为 YU7 增加多个《鬼灭之刃》角色痛车选项，并明确先找帅气热血的图片。本轮范围为来源调查、原图候选和车身构图建议；尚未制作贴图、导入 UE 或实现切换功能。
- 读取 AGENTS.md 与最近 v11 制作/发布历史，初始 git status --short 为空。保持既有地图、资产、模型源和 CREDITS.txt 原文；准备在 art/YU7_ITASHA/references/kimetsu_v01 单独记录候选。
- 已通过网页搜索核对官方《ヒノカミ血風譚2》角色页，首轮候选为炼狱杏寿郎、灶门炭治郎（日之神神乐）、我妻善逸、宇髓天元、富冈义勇。官方角色 PNG 作为人物姿势候选；动画战斗海报作为火焰/雷电/水纹气氛参考。搜索结果不等于已取得贴图使用许可；来源与授权状态分别记录，不沿用汽车模型的许可证。
- web 工具打开游郭篇首页、无穷列车 kv_2.jpg 与旧版义勇 PNG 时返回 Internal Error；未视为图像验收通过。改从已核实的新游戏官方角色页获取图片，后续检查实际像素/尺寸。
- 五张官方新游戏 PNG 均成功下载到 art/YU7_ITASHA/references/kimetsu_v01，并逐张打开查看。原图包含人物和火焰/雷电/刀光/水纹：炼狱1000×782、善逸1000×566、炭治郎1000×742、天元1000×794、义勇1000×558。System.Drawing 解码、尺寸与 SHA-256 复核均通过，五图左上角 alpha=0。未裁剪、编辑或放大原图。新游戏义勇图片的 web 抓取也曾失败，curl 正常取回且本地视觉检查通过。
- sources.json 与 README.txt 已保存官方页面/原图地址、原始哈希、候选配色与放置建议，以及未核实复用许可的状态。建议先做炼狱、善逸、义勇三款，炭治郎和天元为扩展候选；这是设计建议，非用户最终选定。人物有效分辨率受到透明留白限制，未声称这些1000px图片已满足4K车身近景。
- 本轮 git diff --check 通过；仅新增参考目录并追加开发记录，UE资产、历史输出和根署名未修改，无提交/推送。下一步为用户选图后的车身试排、清晰度与投射验证，以及原生Blueprint可选图案实现；均尚未完成。上一条“无穷列车”系文字误写，正确为“无限列车”。

## 2026-10-27 · 炎柱 / 善逸 / 义勇痛车上车 v01（当次记录）

- 用户明确选定三款并授权加入可选图案、放到车上查看效果。本轮制作独立 Itasha_v01 棚拍地图、原生材质与 Variant Manager 选项，提供上车静帧；不要求修改既有18秒交付影片。运行时继续使用原生 Blueprint 可调用接口与材质，Python仅用于编辑器准备/验证。
- 决定以既有 Studio_YU7 棚拍地图作清晰外观比较，先加载并通过 save_map 另存独立地图，再更改新地图。计划用附着车辆的原生 DecalActor 承载左右侧及引擎盖图案，只让漆面接收，图案组与漆面组独立；如实际 Substrate/接收效果不适配，依据检查调整实现，不提前宣称验证通过。
- 已读取 v11/lookdev 指南和历史 Variant Manager 缓存限制。当前没有 Unreal 进程；原工作区只有前轮选图目录和日志修改。tools/yu7_itasha_v01_protect.py 将保护历史资产/媒体与原图，tools/ue_itasha_v01_probe.py 用于只读检查现有车辆及原生贴花接口。最初查询根 ue_jobs 目录失败，已确认真实任务目录为 art/YU7_UNREAL/reports/ue_jobs。
- 789项历史/原图保护快照建立成功。UE启动并只读probe通过，原地图无dirty包；确认9个漆面接收部件均使用稳定原生Actor。首次prepare已另存独立地图、解除新地图旧LVS引用并导入三张原图，在新贴花材质ComponentMask输入连接处停止：实际单输入引脚不叫Input。原图/旧图未改；修正为读取真实输入名，定向重建尚未完成的新材质，不重跑地图/导入创建步骤。
- 定向材质恢复成功，独立 Itasha(None/Rengoku/Zenitsu/Giyu) 与 Paint(三色) 原生选项保存。首轮1080p侧面/前侧MRQ成功（54.90秒、无MRQ错误），但实际查看发现人物呈竖条：probe证实当前Python Rotator位置参数按roll/pitch/yaw映射，侧面投射意外朝上下，视觉不通过。后续改为显式pitch/yaw/roll关键字，并按alpha实际边界在材质UV内裁掉透明留白、捕获比例；源PNG保持原字节。PIL首次alpha分析因源为调色板PNG而失败，转RGBA仅在内存分析后成功。
- v02 四视角MRQ完成（76.75秒、无错误），人物图与原生程序条纹已投射到车身，但侧面人物仍横转90度，不能验收。引擎贴花UV的U/V对应局部Z/Y，已明确修正侧面roll=-90及尺寸轴，按实测alpha边界保持图像宽高比；引擎盖朝向正确，仅更正尺寸比例。新条纹仅由原生材质节点生成，三款分别用红金、黄蓝和蓝青配色。
- v03首次定向修改在重复capture已有属性时返回None而中断；应从get_captured_properties取现有Relative Scale 3D属性再record。随后r03因调度未检查前步失败而渲染了部分修改状态，不能作为v03效果验收。已增加本地任务助手yu7_itasha_job.py等待前轮渲染完成和检查实际job成功；定向v03重试成功，再以新r04名渲染，不覆盖失败证据。
- r04左右/前侧实图暴露两项问题：侧面人物倒置（应roll=+90）；轮胎/轮毂出现条纹。实测旧车Blueprint的121个receives_decals实例值在PIE后全部回到true，原生Actor开关仍有效。采用独立复制BP_YU7_ItashaVehicle，在其组件模板上关闭接收，同时保留全部网格/材质和21个隐藏原分件；新地图中换入该BP，26个原生分件/贴花保持世界变换重新附着。没有修改原BP或网格。
- Blueprint复制后SubobjectData返回每个组件两次，首次数量断言中止；按对象路径去重后121个唯一模板编译/保存、替换与附着成功。新建BP_YU7_ItashaOptions继承LevelVariantSetsActor，提供原生Blueprint的Switch on Variant by Name/Index；当前不新增UMG按钮界面。r05用于验证正向人物及轮胎排除，尚未通过前不开始最终输出。
- r05炎柱四视角、r06善逸三视角、r07义勇三视角原生1080p MRQ均成功，实际逐张查看通过：人物正向、脸部位于单块面板、左右和引擎盖投射成立，轮胎/轮毂不接收贴花。三款分别配珠光白、亮面石墨和矿物青；原棚拍高光仍穿过角色层，源图有效分辨率有限，未声称4K贴图细节。最终侧面roll=+90，前文-90为已修正的过程错误。
- 首次跨帧审计24次（4图案×3车漆×2轮）全部通过，121个唯一可见网格、5贴花附着/移动测试、789历史哈希、原文资产署名和无dirty包通过。结果保留为switch_audit_before_reload.json；清理原lookdev与本轮LVS缓存后，独立地图重载成功，正在执行重载后的审计及真实PIE切换测试，尚未提前标记运行时完成。
- 重载后的首次切换断言失败，已保存switch_audit_reload_failed.json。只读probe显示LVS组仍完整、Blueprint类默认值有引用，但地图实例引用为空；引擎SetLevelVariantSets仅赋值不标记编辑器修改。通过modify/set_editor_property及强制save_map显式持久化场景引用，再按安全顺序重载并复测；未把此前成功的内存内切换等同保存后可用。
- 首次仅强制保存地图的修复仍在重载后失败。进一步将Blueprint类默认引用置空并强制保存Blueprint，随后显式保存地图实例的LVS覆盖；避免实例值与未正确持久化的内存CDO值相同而省略序列化差异。第三次安全重载后24次跨帧切换、789历史哈希和Map Check均通过。实际PIE审计已启动，待独立结果确认。
- 实际PIE（UEDPIE_0_Studio_YU7_Itasha_v01）12种图案/车漆组合全部通过，BP_YU7_ItashaOptions_C原生继承方法驱动5贴花与9漆面槽，BP车辆全部121个模板拒收贴花，5贴花运行时仍附着车辆。Python只作编辑器验证驱动，运行时无Python/C++依赖。开始三款各3视角3840×2160/8时域静帧输出。
- 炎柱4K侧面与前侧已实际查看通过。等待其引擎盖完成时，后续善逸任务助手50秒等待到期，未提交新任务、未中断正在渲染的UE；以异步180秒等待同一完成信号重试，避免并发渲染。20个本轮Python脚本语法检查与受控文本git diff --check通过。
- Final_r08_Rengoku_4K与Final_r09_Zenitsu_4K各3视角MRQ成功（108.97秒、108.90秒，errors=[]），6张原生4K图均实际查看通过；义勇4K正在渲染。保留真实棚拍反射，引擎盖强高光会降低中心人物对比，作为本轮外观预览限制记录。Test_*诊断图片留在本地并加入忽略规则，最终9张4K和验证记录计划保留，不删除失败证据。
- Final_r10_Giyu_4K三视角MRQ成功（153.21秒，errors=[]），三图实际查看通过。全部9张原生4K图已逐张完成视觉检查并写入visual_review.json。三款Variant缩略图使用对应真实Beauty渲染保存，默认回到炎柱/珠光白；最终清LVS缓存重载已成功，跨帧审计正在执行。
- 最终安全重载后24次跨帧切换再次通过，Map Check实际0 Error/0 Warning；789项历史保护哈希全部一致，121唯一可见网格、5贴花附着/移动和空dirty列表通过。yu7_itasha_v01_finish.py完成9张PNG完整解码/尺寸/哈希、51项UE资产清单与21个脚本语法检查。根CREDITS逐字节复制为本轮sidecar，原文件不变；来源与未核实复用许可单独列在ART_SOURCES.txt。README_UE和AGENTS记录实际入口、切换方式与局限。未提交/推送；应用内可见Credits与打包/新机器验证仍未标记完成。
- 已核实重载后三款缩略图与场景LVS引用有效，并成功请求打开原生Variant Manager选项面板，视口恢复Beauty机位。最终git diff --check通过（仅CRLF规范化提示），本地编辑器任务轮询停止请求已发送；该stop分支本来不生成结果JSON，不将其视为额外验证回执。

## 2026-10-28 · 痛车 v01 Git 发布（当次记录）

- 用户明确要求推送到Git。本轮提交既有炎柱/善逸/义勇痛车资产、9张4K效果图、来源、工具与验证记录；不重跑UE制作或渲染。初始分支main，HEAD=a08be8e，origin为https://github.com/VegaBai/vehicle-visualization.git；待提交改动均属于本轮痛车制作，先核对交付哈希、历史保护、暂存范围与LFS，再正常推送，不强制覆盖远端。
- 首次git fetch因沙箱只读.git而无法写FETCH_HEAD，后续使用受审查的Git写权限重试；该次0/0计数基于旧远端引用，未视为已刷新。发布完整性检查已通过61项交付与789项历史哈希，但排除规则误将reports中的Test_*状态JSON当作诊断图片，断言中止；收窄为renders下Test_*目录，保留过程验证JSON后重查。
- git fetch重试成功。61项交付（51项UE资产、9张4K图、署名）与789项历史保护SHA256一致，署名sidecar原字节一致。161项新制作文件共83,502,874 bytes，70个JSON与21个Python解析通过，96份文本常见凭据签名无匹配；诊断试图/UE缓存均不在候选范围。证据保存publication_preflight.json，本轮只核对既有验证记录与完整性，不冒称重新运行UE或打包测试。
- 刷新后的HEAD与origin/main均为a08be8e，0 ahead / 0 behind。166个文件已暂存，其中65项LFS指针的SHA256和size与本地二进制逐项一致，逻辑总量约83.65MB，最大普通Git对象146,411 bytes；暂存差异检查通过，无剩余未暂存/未跟踪改动，Test_*图片忽略规则生效。将以“Add Demon Slayer itasha options and 4K studio previews”提交并正常推送main。
- 制作成果提交39a9f5cda6555f3b9ddf6003d9f419fa20debd5d已成功推送origin/main，166个文件、65项LFS对象约83MB全部上传完成。git lfs fsck HEAD返回OK；git ls-remote核实远端main与该提交完全一致，git lfs push --dry-run origin main没有待上传对象。成果推送后工作区为空；本条与publication_remote_verification.json作为随后独立的发布记录提交同步，不重写制作成果提交。
