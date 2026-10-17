import bpy,json,math
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\github2\vehicle_visualization');OUT=ROOT/'art/YU7_UNREAL'
scene=bpy.context.scene
vehicles=[o for o in scene.objects if o.type=='MESH']
vehicle_collection=bpy.data.collections.new('YU7_VEHICLE');scene.collection.children.link(vehicle_collection)
for o in vehicles:
    for col in list(o.users_collection):col.objects.unlink(o)
    vehicle_collection.objects.link(o)
for o in list(scene.objects):
    if o.type=='EMPTY':bpy.data.objects.remove(o,do_unlink=True)
for s in list(bpy.data.scenes):
    if s!=scene:
        for o in list(s.objects):bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.scenes.remove(s)

# Studio rig is only for inspection and is excluded from the FBX selection.
rig=bpy.data.collections.new('AUDIT_STUDIO_NOT_EXPORTED');scene.collection.children.link(rig)
def move_to_rig(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    rig.objects.link(o)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004))
floor=bpy.context.object;floor.name='AUDIT_FLOOR';move_to_rig(floor)
mat=bpy.data.materials.new('AUDIT_FLOOR');mat.use_nodes=True
p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.055,.06,.07,1);p.inputs['Roughness'].default_value=.35
floor.data.materials.append(mat)
def area(name,loc,power,size,size_y,target=(0,0,.8)):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='RECTANGLE';data.size=size;data.size_y=size_y
    o=bpy.data.objects.new(name,data);rig.objects.link(o);o.location=loc;aim(o,target)
area('AUDIT_KEY',(1,-4,6),1600,6,2)
area('AUDIT_RIM',(-2,4,4.5),2100,6,1)
area('AUDIT_FRONT',(5,2,3.5),900,3,2)
world=bpy.data.worlds.new('YU7_AUDIT_WORLD');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.12,.14,.18,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.4;scene.world=world
cam_data=bpy.data.cameras.new('AUDIT_CAMERA');cam=bpy.data.objects.new('AUDIT_CAMERA',cam_data);rig.objects.link(cam)
cam.location=(7,-8,3.4);aim(cam,(0,0,.8));cam_data.lens=55;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU'
except Exception:scene.cycles.device='CPU'
scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.filepath=str(OUT/'reports/preview_front.png')
scene.view_settings.view_transform='AgX'
scene.render.image_settings.color_mode='RGB'

for o in scene.objects:o.select_set(False)
for o in vehicles:o.select_set(True)
bpy.context.view_layer.objects.active=vehicles[0]
settings=dict(filepath=str(OUT/'YU7_Unreal.fbx'),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',use_space_transform=True,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_tspace=True,use_triangles=True,use_custom_props=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',embed_textures=False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'YU7_Prepared.blend'),check_existing=False)
bpy.ops.export_scene.fbx(**settings)
(OUT/'reports/export_settings.json').write_text(json.dumps({**settings,'object_types':['MESH']},indent=2),encoding='utf-8')
print(json.dumps({'blend':str(OUT/'YU7_Prepared.blend'),'fbx':str(OUT/'YU7_Unreal.fbx'),'meshes':len(vehicles),'device':scene.cycles.device}))
