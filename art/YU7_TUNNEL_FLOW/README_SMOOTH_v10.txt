YU7 ROOF AIRFLOW — SMOOTH v10
2026-10-19

Purpose
User identified a sharp bend in the v09 roof airflow. Curves should pass smoothly
over small body details instead of reproducing radar/roof-envelope corners.

Isolated working assets
/Game/YU7/TunnelFlow/RoofSmooth_v10/Maps/Studio_YU7_TunnelFlow_Smooth_v10
/Game/YU7/TunnelFlow/RoofSmooth_v10/Sequences/LS_YU7_TunnelFlow_Smooth_v10_12s
/Game/YU7/TunnelFlow/RoofSmooth_v10/Blueprints/BP_TunnelRoofAirflow_Smooth_v10
Prepared: prepared/YU7_RoofAirflow_Smooth_v10.blend and .fbx
Reports: reports/roof_smooth_v10
Media: renders/YU7_TunnelFlow/RoofSmooth_v10 (repository root)

Geometry
Seven separate meshes; 92,400 triangles. Same UV progress, lane identifiers and
5.2 mm primary / 3 mm secondary line diameters as v09. Broad Gaussian height
smoothing (sigma 35 cm, linear endpoint extension) plus uniform 2.5 cm lift.
No pointwise clamp to fine body details. Native WPO and all shading are reused
unchanged from v09; camera, lighting, mineral-teal paint, grid and timing retained.

Completed delivery and validation
Final_r03_4K_12s.mp4: native 3840x2160, 24 fps, 288 frames, 12 seconds,
8 temporal samples, silent. Native MRQ completed in 679.43 seconds with no errors.
Previs_r02_1080p_12s.mp4: native 1920x1080 with the same timing/sample count.
All native PNG frames and both complete MP4 decodes passed.
Seven curated 4K stills are unmodified copies of final frames 24/96/122/163/222/269/287.
RoofCurve_Before_After.png compares native-pixel crops at frame 96 (v09 above,
v10 below); it is an inspection derivative. The delivered frame files are intact.
All-frame contact sheets, roof detail strips and full-resolution stills were
visually inspected; no claim of realtime player viewing or human acceptance.
Authored geometry, imported copies and final safe save/reload audit passed.
Map Check: 0 errors / 0 warnings; dirty map/content package lists empty.
3,010,483 closest-triangle samples over 12 seconds at 96 Hz:
minimum dynamic clearance 13.684965 cm; minimum static clearance 16.316217 cm.
Samples include all 121 vehicle meshes and tube radius. Maximum WPO 17.9223 cm,
native cap 25 cm, bounds scale 1.5. Illustrative curves, not CFD or a continuous
collision guarantee. See reports/roof_smooth_v10/output_manifest.json,
visual_review.json, scene_audit.json and per-output status/validation records.
Final video SHA256:
036db47cf4b741acfe803d25854a67d6019ccebd9b91d8d87db5b1d56338f4a4

Preservation and runtime
658 prior source/asset/media/report files protected, including v09 delivery.
Original v09 roof actor hidden only in the new map; v09 map remains unchanged.
121 original visible vehicle meshes, full 99,916-triangle body quad, unattached
world wake and two-primary/five-secondary hierarchy remain.
Do not rerun one-time preparation scripts over existing assets.
Clear LVS cache before map reload, as documented in README_AD_v09.txt.
All runtime behavior is Blueprint, Sequencer and native material nodes.
Python scripts only prepare and validate assets offline/in the editor.
Exact attribution is in CREDITS.txt, asset metadata and delivery video metadata.
Application Credits UI and packaged/new-machine validation remain final-project
delivery items. New paint finishes await reference images; shot remains silent.
