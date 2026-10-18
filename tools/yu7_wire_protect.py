"""Capture originals before the isolated quad display study. Run outside UE."""
import hashlib,json
from pathlib import Path
ROOT=Path('C:/github2/vehicle_visualization')
OUT=ROOT/'art/YU7_WIREFRAME/reports'
OUT.mkdir(parents=True,exist_ok=True)
dest=OUT/'protected_before.json'
assert not dest.exists(), 'Preserve the original baseline'
paths=[]
for folder in ['art/FINAL_MODEL','art/YU7_UNREAL','VehicleStudio/Content']:
    paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() in {'.fbx','.blend','.png','.jpg','.jpeg','.webp','.uasset','.umap'})
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
dest.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with (ROOT/'DEV_HISTORY.md').open('a',encoding='utf-8') as f:
    f.write('\n### 32 · 引擎盖与前翼子板 quad 线框试作开始（当次记录）\n\n- 用户已授权在引擎盖与前翼子板制作矿物青车漆叠加稀疏 quad 线的第一版，并要求保留现有场景和模型。将使用 art/YU7_WIREFRAME、/Game/YU7/WireframeStudy 与 renders/YU7_WireframeStudy 独立输出。\n- 已读取现有 lookdev/hero 指南、脚本及状态。现有 Blender MCP 正在打开 YU7_Prepared.blend，宿主仅一个 UnrealEditor 进程；准备使用既有编辑器而非并行启动。\n- 创建 art/YU7_WIREFRAME/reports/protected_before.json，记录 '+str(len(manifest))+' 个既有模型、纹理、UE 内容文件的 SHA256。保护快照为本轮新生成，最终需复核。\n- 采用离线采样贴合的细线几何，作为独立普通静态网格叠加；不改原车身拓扑、法线、UV 和材质。展示线网将另存，不宣称还原源拓扑。Python 仅用于编辑器准备与验证，无运行时依赖，尚未生成或验证最终效果。\n')
print(json.dumps({'protected':len(manifest),'manifest':str(dest)}))
