YU7 / QUAD SURFACE STUDY / 2026-10-17

Purpose
-------
Mineral teal paint with sparse surface-flow lines on the bonnet and both front
fenders. This is an authored quad-looking display overlay, not recovered source
topology and not a CAD curvature-analysis result. Only the overlay is new.

Open in Unreal 5.8
-----------------
Map: /Game/YU7/WireframeStudy/Maps/Studio_YU7_QuadStudy
Sequences: /Game/YU7/WireframeStudy/Sequences/LS_YU7_Quad_Overview
           /Game/YU7/WireframeStudy/Sequences/LS_YU7_Quad_Detail
Active line meshes: /Game/YU7/WireframeStudy/Meshes/v03
Material instance: /Game/YU7/WireframeStudy/Materials/MI_QuadLines_IceTeal

The three YU7_Quad_* StaticMeshActors are attached to the existing YU7_Hero in
the study map. Original car parts remain intact. Hide the three overlay actors
to see the original paint. Set Hidden in Game as well when rendering in MRQ.
LineColor and LineBrightness are editable material-instance parameters.
The material uses ordinary opaque unlit rendering; native Wireframe is OFF.
This avoids showing triangulation diagonals. Brightness is authored for the
existing EV9 / exposure-bias +1 studio, not calibrated physical emission.

Prepared assets
---------------
YU7_QuadStudy_v03.blend: derivative working scene, old v01/v02 overlays hidden.
YU7_QuadLines_v03.fbx: only the three new fine-line meshes, in source coordinates.
v01/v02 files and preview renders are retained as iteration evidence.
Tube diameter: 1.5 mm. Sampled centre offset: approximately 1.1 mm.
Bonnet: 15 longitudinal rails crossed by 10 contour rows, interrupted at holes.
Fenders: 13 spokes crossed by three smooth curves on the painted arch band.
All are sampled on the existing paint mesh. Fine geometry allows smooth curves
while the visible cell spacing remains sparse. No original normals or UVs changed.

Validation and outputs
----------------------
Actual final MRQ completion: reports/Final_v03_Confirmed_status.json.
Saved-map audit: reports/final_scene_audit.json.
Source hash and image decoding: reports/delivery_validation.json.
Do not infer verification from this guide if those reports are absent or failed.
Final outputs: renders/YU7_WireframeStudy/Final_v03_Confirmed (two 4K stills).
Final_v03 is the earlier 4K visual check before parenting/persistence repairs.
Native MRQ presets are under /Game/YU7/WireframeStudy/RenderPresets.
No generated-image retouch or compositing is used; the images are native UE MRQ.
This study is for still-image review. It does not claim motion flicker testing,
packaged-build testing, or completion of the final in-application Credits UI.

Editor workflow
---------------
tools/yu7_wire_build.py prepares offline geometry in Blender; it refuses to
overwrite its versioned FBX. One-time UE prepare/import scripts also guard
against overwriting existing assets. Do not blindly rerun them.
Python is only an editor preparation/validation tool. No runtime Python or C++
was added. The original lookdev Variant Manager cache restrictions still apply;
always clear the LVS package before reloading a map, or restart the editor.
The study retains the hero map's intentionally unbound VariantManager.
The overlay components must be Movable to attach to the vehicle's Movable root.
Use the NoCollision profile, not only set_collision_enabled, for persistence.

Exact source attribution
------------------------
"2025 Xiaomi YU7" (https://skfb.ly/pCSLu) by Ddiaz Design is licensed under CC Attribution-NonCommercial-ShareAlike (http://creativecommons.org/licenses/by-nc-sa/4.0/).
