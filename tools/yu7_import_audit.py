import bpy
import json
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(r"C:\github2\vehicle_visualization")
SOURCE = ROOT / "art/FINAL_MODEL"
OUT = ROOT / "art/YU7_UNREAL"
(OUT / "reports").mkdir(parents=True, exist_ok=True)
manifest = {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in SOURCE.iterdir() if p.is_file()}
(OUT / "reports/source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

scene = bpy.data.scenes.new("YU7_PREP")
bpy.context.window.scene = scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
bpy.ops.import_scene.fbx(filepath=str(SOURCE / "FINAL_MODEL.fbx"), use_custom_normals=True, use_image_search=True)
meshes = [o for o in scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
minimum = [min(p[i] for p in pts) for i in range(3)]
maximum = [max(p[i] for p in pts) for i in range(3)]
objects = []
for o in meshes:
    m = o.data
    m.calc_loop_triangles()
    objects.append({"name": o.name, "parent": o.parent.name if o.parent else None, "vertices": len(m.vertices), "polygons": len(m.polygons), "triangles": len(m.loop_triangles), "dimensions": list(o.dimensions), "location": list(o.matrix_world.translation), "scale": list(o.scale), "determinant": o.matrix_world.determinant(), "custom_normals": m.has_custom_normals, "smooth_faces": sum(p.use_smooth for p in m.polygons), "uv_layers": [u.name for u in m.uv_layers], "materials": [s.material.name if s.material else None for s in o.material_slots], "modifiers": [(x.name,x.type) for x in o.modifiers]})
mats = []
for mat in {s.material for o in meshes for s in o.material_slots if s.material}:
    mats.append({"name": mat.name, "diffuse": list(mat.diffuse_color), "metallic": mat.metallic, "roughness": mat.roughness, "nodes": [{"name":n.name,"type":n.type,"image": n.image.name if n.type=="TEX_IMAGE" and n.image else None} for n in mat.node_tree.nodes] if mat.use_nodes else [], "links": [(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links] if mat.use_nodes else []})
images = [{"name":i.name,"filepath":i.filepath,"exists":Path(bpy.path.abspath(i.filepath)).is_file() if i.filepath else False,"size":list(i.size),"colorspace":i.colorspace_settings.name,"packed":bool(i.packed_file)} for i in bpy.data.images if i.source=="FILE"]
report={"blender":bpy.app.version_string,"bounds_min":minimum,"bounds_max":maximum,"dimensions": [maximum[i]-minimum[i] for i in range(3)],"scene_unit_scale":scene.unit_settings.scale_length,"objects":objects,"materials":mats,"images":images,"totals":{"meshes":len(meshes),"vertices":sum(x['vertices'] for x in objects),"triangles":sum(x['triangles'] for x in objects),"materials":len(mats)}}
(OUT / "reports/import_audit.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
for a in bpy.context.screen.areas:
    if a.type == "VIEW_3D":
        with bpy.context.temp_override(area=a,region=next(r for r in a.regions if r.type=="WINDOW")):
            bpy.ops.view3d.view_all(center=False)
print(json.dumps({k:report[k] for k in ['totals','dimensions','bounds_min','bounds_max']},indent=2))
print(json.dumps({"objects":[{k:o[k] for k in ['name','triangles','dimensions','location','scale','custom_normals','uv_layers','materials']} for o in objects],"images":images},indent=2))
