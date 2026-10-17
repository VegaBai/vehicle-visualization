import bpy, json, re
from pathlib import Path

ROOT=Path(r'C:\github2\vehicle_visualization')
OUT=ROOT/'art/YU7_UNREAL'
scene=bpy.context.scene
meshes=[o for o in scene.objects if o.type=='MESH']
fallbacks={}
for o in meshes:
    if not o.get('generated_uv_requires_solid_material'):continue
    for slot in o.material_slots:
        mat=slot.material
        p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if p and p.inputs['Base Color'].is_linked:
            if mat.name not in fallbacks:
                copy=mat.copy();copy.name=mat.name+'__UVFallback';copy['uv_fallback_source']=mat.name
                fallbacks[mat.name]=copy
            slot.material=fallbacks[mat.name]

def image_for(filename,data=False):
    key=filename+('_DATA' if data else '_COLOR')
    img=bpy.data.images.get(key)
    if img is None:
        img=bpy.data.images.load(str(OUT/'Textures'/filename),check_existing=False)
        img.name=key
    img.colorspace_settings.name='Non-Color' if data else 'sRGB'
    return img

manifest=[]
materials=sorted({s.material for o in meshes for s in o.material_slots if s.material},key=lambda m:m.name)
for mat in materials:
    source=mat.name
    original=mat.get('uv_fallback_source',source)
    old_p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    linked=old_p.inputs['Base Color'].links
    texname=Path(linked[0].from_node.image.filepath).name if linked and linked[0].from_node.type=='TEX_IMAGE' else None
    color=list(old_p.inputs['Base Color'].default_value)[:3] if not texname else [1.,1.,1.]
    metal,rough,coat,coatrough=0.,.45,0.,.12
    transmission,opacity=0.,1.
    normal=None;mask=False
    if original=='CarPaint':metal,rough,coat=.25,.28,1.
    elif original=='Blaack_Paint':color=[.012,.014,.017];metal,rough,coat=.15,.27,1.
    elif original=='Black_Mat':color=[.012,.012,.012];rough=.58
    elif original in ['Windows','D_Glass','Light_Glass']:
        color=[.92,.96,1.];metal=0.;rough=.055;transmission=1.
        opacity={'Windows':.25,'D_Glass':.42,'Light_Glass':.12}[original]
    elif original=='Mirrors':color=[.85,.85,.85];metal,rough=1.,.045
    elif original=='ALUM':color=[.55,.55,.55];metal,rough=1.,.25
    elif original in ['Yu7:RIM_C1','RIM_C2']:
        color=[.018,.02,.025] if original=='Yu7:RIM_C1' else [.3,.32,.34]
        metal,rough=1.,.26
    elif original in ['Caliper_C1','Caliper_C2']:metal,rough=.4,.32
    elif original=='DISK':metal,rough=1.,.38
    elif original=='Metal_Mat':color=[.055,.055,.055];metal,rough=.8,.45
    elif original=='LIGHT_CHROME_SH':metal,rough=.95,.18
    elif original=='LIGHT_PLASTIC_SH':metal,rough=0.,.24
    elif original=='Plastic_SH':metal,rough,coat=0.,.26,.35
    elif original=='dark_Gray_Map':metal,rough=0.,.55
    elif original=='tyre_3':
        texname='carTyre_02_ao.png';color=[.024,.026,.028];metal,rough=0.,.65
        normal='T_YU7_Tyre_Normal_DX.png'
    elif original.lower().startswith('int_'):metal,rough=0.,.65
    elif original=='CAR_L':metal,rough=0.,.22
    else:metal,rough=0.,.5
    fallback=bool(mat.get('uv_fallback_source'))
    if fallback:
        texname=None
        color=[.65,.65,.65] if original=='CarPaint' else [.055,.025,.012]
    if texname in ['carLightShape.png','carHoodOutletPanelShape.png','carPlastic_BrilliantBlackShape.png']:mask=True
    mat.name='M_YU7_'+re.sub('[^A-Za-z0-9_]','_',source)
    mat['source_material_name']=source
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;nodes.clear()
    output=nodes.new('ShaderNodeOutputMaterial');output.location=(600,0)
    p=nodes.new('ShaderNodeBsdfPrincipled');p.location=(240,0)
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Coat Weight'].default_value=coat;p.inputs['Coat Roughness'].default_value=coatrough
    p.inputs['Transmission Weight'].default_value=transmission;p.inputs['IOR'].default_value=1.45 if transmission else 1.5
    p.inputs['Emission Strength'].default_value=0.
    links.new(p.outputs['BSDF'],output.inputs['Surface'])
    if texname:
        im=nodes.new('ShaderNodeTexImage');im.image=image_for(texname,data=(original=='tyre_3'));im.location=(-600,160)
        if color!=[1.,1.,1.]:
            mult=nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1.;mult.inputs[2].default_value=(*color,1);mult.location=(-100,160)
            links.new(im.outputs['Color'],mult.inputs[1]);links.new(mult.outputs[0],p.inputs['Base Color'])
        else:links.new(im.outputs['Color'],p.inputs['Base Color'])
        if mask:links.new(im.outputs['Alpha'],p.inputs['Alpha'])
    if normal:
        im=nodes.new('ShaderNodeTexImage');im.image=image_for('T_YU7_Tyre_Normal_GL.png',True);im.location=(-600,-200)
        nm=nodes.new('ShaderNodeNormalMap');nm.uv_map='UV0';nm.location=(-100,-200)
        links.new(im.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],p.inputs['Normal'])
    mat.diffuse_color=(*([.08,.11,.14] if transmission else color),opacity if transmission else 1.)
    mat.metallic=metal;mat.roughness=rough
    mat.use_backface_culling=False
    if hasattr(mat,'surface_render_method'):mat.surface_render_method='DITHERED'
    manifest.append({'name':mat.name,'source_material':source,'base_color_linear':color,'base_texture':texname,'base_texture_data':original=='tyre_3','metallic':metal,'roughness':rough,'clear_coat':coat,'clear_coat_roughness':coatrough,'normal_texture_dx':normal,'blend_mode':'TRANSLUCENT' if transmission else 'MASKED' if mask else 'OPAQUE','opacity':opacity,'ior':1.45 if transmission else 1.5,'ue_glass_color_linear':[.08,.11,.14] if transmission else None,'emission_strength':0,'uv_fallback':fallback})
mesh_manifest=[{'mesh':o.name,'source':o['source_object_name'],'material_slots':[s.material.name for s in o.material_slots]} for o in meshes]
(OUT/'materials.json').write_text(json.dumps({'materials':manifest,'meshes':mesh_manifest},indent=2),encoding='utf-8')
for img in {n.image for mat in materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}:
    filename=img.name.removesuffix('_DATA').removesuffix('_COLOR')
    img.filepath=str(OUT/'Textures'/filename)
    img.pack()
    img.filepath='//Textures/'+filename
credits=(ROOT/'CREDITS.txt').read_text(encoding='utf-8')
text_block=bpy.data.texts.get('CREDITS.txt') or bpy.data.texts.new('CREDITS.txt');text_block.clear();text_block.write(credits)
scene['asset_credit']=credits.strip();scene['asset_license']='CC BY-NC-SA 4.0';scene['prepared_for']='Unreal static cinematic asset; +X forward, +Z up; meters'
for o in meshes:o.select_set(False)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.clip_start=.01;a.spaces.active.clip_end=1000
        a.spaces.active.shading.type='MATERIAL'
        with bpy.context.temp_override(area=a,region=next(r for r in a.regions if r.type=='WINDOW')):bpy.ops.view3d.view_all(center=False)
print(json.dumps({'materials':len(manifest),'fallback_materials':[m['name'] for m in manifest if m['uv_fallback']],'masked_materials':[m['name'] for m in manifest if m['blend_mode']=='MASKED'],'glass_materials':[m['name'] for m in manifest if m['blend_mode']=='TRANSLUCENT'],'referenced_textures':len({n.image.name for mat in materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image})},indent=2))
