YU7 / FULL BODY QUAD SURFACE STUDY / 2026-10-17

Purpose
-------
Extends the approved bonnet/front-fender concept over the exterior painted
body, with aligned lines across panel seams. This is an authored quad-looking
display field, not recovered source topology. The vehicle geometry is intact.
Glass, lights, wheels, tyres and black trim retain their original appearance.
The mirror shells have separate small quad fields. Real panel gaps stay open.

Unreal 5.8 entry points
----------------------
Map: /Game/YU7/QuadBodyStudy/Maps/Studio_YU7_QuadBody
Sequences: /Game/YU7/QuadBodyStudy/Sequences/LS_YU7_BodyQuad_Overview
           /Game/YU7/QuadBodyStudy/Sequences/LS_YU7_BodyQuad_Detail
           /Game/YU7/QuadBodyStudy/Sequences/LS_YU7_BodyQuad_Rear
Active line meshes: /Game/YU7/QuadBodyStudy/Meshes/v03
Material: /Game/YU7/QuadBodyStudy/Materials/MI_BodyLines_IceTeal

YU7_BodyQuad_Body, YU7_BodyQuad_Mirror_L and YU7_BodyQuad_Mirror_R are
Movable native StaticMeshActors attached to YU7_Hero with NoCollision profile.
Hide these three actors to view the original paint. The earlier YU7_Quad_*
actors are retained but their components are invisible in this new map.
The accepted local study map remains unchanged in /Game/YU7/WireframeStudy.
LineColor/LineBrightness are adjustable on the new material instance. The
parent is the existing opaque Unlit M_QuadLines, native Wireframe OFF.
Brightness 100 is authored for this studio's exposure, not physical emission.

Prepared source and generation
------------------------------
YU7_BodyStudy_v03.blend / YU7_BodyLines_v03.fbx are the current editable source
and overlay-only FBX. Prior study collections are hidden in the new Blend.
tools/yu7_body_build.py creates versioned geometry and refuses an existing FBX.
The closed six-face cage shares edge coordinates, avoiding triangular pole
fans. Rays are clipped to the outermost vehicle surface and paint material.
Line diameter 1.5 mm; sampled centre offset 1.1 mm. Offline simplification has
a 0.1 mm sampled-curve error limit. Four spans crossing narrow gaps were removed.
Final overlay: 99,916 render triangles, approximately 89.4% fewer than v01.
These triangles form thin tubes; they are not visible wireframe diagonals.
The visible grid is deliberately sparse. No original mesh UVs/normals changed.

Evidence and limits
-------------------
reports/geometry_v03.json and geometry_fit_v03.json: offline geometry checks.
reports/pre_render_audit.json: saved/reloaded scene before final rendering.
reports/Final_v03_status.json: actual MRQ completion status.
reports/Final_v03_validation.json: PNG decoding and 393 protected-file hashes.
reports/final_scene_audit.json: saved/reloaded final state and preset checks.
Only successful reports establish completion; guide text alone is not evidence.
Final images: renders/YU7_QuadBodyStudy/Final_v03 (front, detail and rear).
Images are native UE MRQ outputs with no AI retouch or compositing.
Still-image study only; animation flicker and packaged interaction are untested.
Python is editor preparation only; no runtime Python or C++ was added.
Final in-application Credits UI remains pending; sidecars do not replace it.

Map reload safety
-----------------
Save and reload LVS_YU7_Lookdev's package before reloading a map, or restart
the editor. The existing UE 5.8 Variant Manager cache workaround still applies.
The new map inherits the hero map's intentionally unbound Variant Manager.
Do not rerun one-time preparation/import scripts on existing asset paths.

Exact attribution
-----------------
"2025 Xiaomi YU7" (https://skfb.ly/pCSLu) by Ddiaz Design is licensed under CC Attribution-NonCommercial-ShareAlike (http://creativecommons.org/licenses/by-nc-sa/4.0/).
