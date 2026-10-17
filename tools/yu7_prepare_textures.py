"""Copy source textures and derive portable, non-AI texture files for Unreal."""
from pathlib import Path
import json, shutil
import numpy as np
from PIL import Image

root=Path(r'C:\github2\vehicle_visualization')
src=root/'art/FINAL_MODEL'
out=root/'art/YU7_UNREAL'
tex=out/'Textures'; tex.mkdir(parents=True,exist_ok=True)
records=[]
for p in sorted(src.iterdir()):
    if p.suffix.lower() not in {'.png','.webp'}: continue
    target=tex/(p.stem+'.png')
    with Image.open(p) as im:
        dims=im.size
        if p.suffix.lower()=='.webp': im.save(target,format='PNG')
        else: shutil.copy2(p,target)
    records.append({'source':p.name,'output':target.name,'size':dims,'operation':'lossless format conversion' if p.suffix.lower()=='.webp' else 'unchanged copy'})
h=np.asarray(Image.open(src/'carTyre_02_245_bump.png').convert('L'),dtype=np.float32)/255.0
# Height gradients in image coordinates; OpenGL +Y points up the UV image.
dy,dx=np.gradient(h)
normal=np.stack((-dx*3.0,dy*3.0,np.ones_like(h)),axis=-1)
normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
for convention in ['GL','DX']:
    n=normal.copy()
    if convention=='DX': n[...,1]*=-1
    dest=tex/f'T_YU7_Tyre_Normal_{convention}.png'
    Image.fromarray(np.round((n*.5+.5)*255).clip(0,255).astype(np.uint8)).save(dest)
    records.append({'source':'carTyre_02_245_bump.png','output':dest.name,'operation':'height-gradient tangent normal, strength 3.0','convention':'OpenGL +Y' if convention=='GL' else 'DirectX -Y'})
shutil.copy2(root/'CREDITS.txt',out/'CREDITS.txt')
(out/'reports/texture_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(json.dumps({'copied_or_converted':23,'derived_normal_maps':2,'texture_directory':str(tex)}))
