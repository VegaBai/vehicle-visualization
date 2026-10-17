YU7 MINERAL TEAL / HERO SHOT / 2026-10-17

Scope and current verification
------------------------------
This shot is an isolated cinematic scene. The original Studio_YU7 lookdev map,
LVS variants, imported vehicle assets, Studio_White and source files are preserved.
For actual render completion, consult reports/hero/*_status.json; for final
verification consult delivery_validation.json and final_scene_audit.json.
Do not infer successful output merely from the presence of a render preset.

Unreal assets
-------------
Map: /Game/YU7/Cinematics/Maps/Studio_YU7_MineralHero
Camera: CAM_YU7_MineralHero
Sequence: /Game/YU7/Cinematics/Sequences/LS_YU7_MineralHero_5s
Materials: /Game/YU7/Cinematics/Materials
Presets: /Game/YU7/Cinematics/RenderPresets
  MRQ_YU7_MineralTeal_4K
  MRQ_YU7_MineralTeal_Motion_4K

The shot uses the 21 existing native vehicle parts plus 100 visible Blueprint
parts. Eight native RectLights light the vehicle and backdrop. The old lighting
Blueprint remains disabled. The shot's VariantManager has no LVS assigned:
it is a fixed teal composition, and does not switch back to original-map bindings.

Camera and light direction
--------------------------
68 mm on a 36 x 20.25 mm sensor, aperture f/8 with depth of field disabled.
The whole vehicle remains legible. A 7.5-degree eased camera arc with a 30 cm
push-in and 8 cm descent runs over 120 frames at 24 fps. Native transform keys
have pre/post handles; no runtime Python or C++ is needed for playback.
The frame-zero camera is the hero still. Re-open the sequence at frame zero
to inspect the exact composition.

Large source reflections are reduced through light placement and intensity.
Low specular-scale fill lights deliberately provide separate dark-area control.
The overhead fill has SpecularScale=0: this is an artistic studio-light choice.
Glass remains Thin Translucent with OpaqueLayerAmount=0 and SurfaceCoverage=1.
Tint and Specular=0.4 are set on a copied instance; original glass is untouched.
The color is an artistic mineral-teal finish, not a claimed official paint code.
Final applied settings: reports/hero/v4_settings.json.

Re-render without scripts
------------------------
1. Open the cinematic map above, then the LS_YU7_MineralHero_5s sequence.
2. Open Movie Render Queue, add that sequence, and choose the matching preset.
3. Confirm the job's map is Studio_YU7_MineralHero and choose a new output folder.
4. For the still, use custom frame range [0,1), 3840x2160, 64 spatial x 1 temporal.
   For motion, use [0,120), 3840x2160, 1 spatial x 16 temporal, 24 fps.
5. Both presets use 64 engine warm-up and 32 render warm-up samples, AA None,
   screen percentage 100, hardware-ray-traced Lumen and native MRQ output.
   Still motion blur is 0; motion override is 0.25.

At 4K the engine clamps the requested Lumen screen-probe downsample factor 2
to 8 because of its maximum 2D texture atlas size. This is the actual tested
rendering path; the higher requested probe density is not achieved.

Delivery files
--------------
Project-root renders/YU7_MineralHero:
  YU7_MineralTeal_4K.png             display-ready 3840x2160 still
  YU7_MineralTeal_4K.exr             half-float MRQ still, default tone curve
  YU7_MineralTeal_5s_4K.mp4          H.264 viewing copy, 120 frames, 24 fps
  frames/                          original MRQ PNG frames 0000-0119
  still/                           original MRQ PNG and EXR
  CREDITS.txt                      exact attribution

The EXR preserves MRQ's default UE tone curve. It is not an un-tonemapped,
raw scene-linear grading master. No AI retouching or external pixel editing
is applied to the still or the source video frames. MP4 is encoded from them.
The video is a silent camera/lighting test; no music or final title edit is added.

Editor helpers and safety
-------------------------
tools/ue_hero_prepare.py and ue_hero_sequence.py are one-time preparation scripts.
They refuse to overwrite the existing map/sequence; do not blindly rerun them.
ue_hero_adjust.py applies a named configuration ONLY to the isolated cinematic map.
ue_hero_render.py submits MRQ and saves a uniquely named preset and status record.
These are editor helpers, not runtime dependencies. package_hero_delivery.py
validates PNG frames, encodes MP4 and checks original-file hashes. Its FFmpeg
dependency is local under tools/vendor and is not shipped into the UE runtime.

Original lookdev-map reload restrictions in LOOKDEV_GUIDE.txt still apply.
This cinematic work does not claim PIE configurator or packaged-build testing.
The visible Credits screen in the final UE application remains a later delivery
item. Sidecar/metadata credits here do not replace that requirement.

Attribution
-----------
"2025 Xiaomi YU7" (https://skfb.ly/pCSLu) by Ddiaz Design is licensed under CC Attribution-NonCommercial-ShareAlike (http://creativecommons.org/licenses/by-nc-sa/4.0/).
