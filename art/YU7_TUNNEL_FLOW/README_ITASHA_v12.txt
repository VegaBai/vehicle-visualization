YU7 — PAINT, ITASHA AND FLOW v12
2026-11-18 / UE 5.9

Request
Add existing itasha and paint switching to the latest finish/flow film.
Original 18s v11 film and all historical assets/media remain preserved.

Editable project
VehicleStudio_UE59/VehicleStudio.uproject only. VehicleStudio is frozen UE5.8.
/Game/YU7/TunnelFlow/ItashaShowcase_v12/Maps/Studio_YU7_ItashaShowcase_v12
/Game/YU7/TunnelFlow/ItashaShowcase_v12/Sequences/LS_YU7_ItashaShowcase_v12_24s

Timeline (24fps / 576 frames / 24 seconds)
0–6s: existing grey-blue gloss, blue metallic, white pearl, graphite matte,
      porcelain grey gloss showcase. Six-frame eased finish transitions.
6–8s: Rengoku / pearl white; visible decal frames 150–191.
8–10s: Zenitsu / graphite; visible decal frames 198–239.
10–12s: Giyu / mineral teal; visible decal frames 246–287.
Each stage begins with a six-frame paint change before the decal appears.
12–24s: decals hidden; original mineral-teal flow, roof pulse, quad and clean exit.
The v11 camera/car/wheel/light/ShotTime animation samples source f/2 until new
frame 288, then source f-144. Motion is continuous; original flow-phase timing
is shifted six seconds. No frame-wide dissolves or image-composited decals.

Implementation
Copied vehicle Blueprint preserves 121 component templates while rejecting decals.
Four copied wheel Blueprints reject decals on all 24 spinning mesh templates.
Nine existing native paint receivers accept the original character/stripe materials.
Fifteen native decal Actors (five per character) attach to the new hero and use
their final v01 relative transforms, including the correct side roll and UV aspect.
Sequencer visibility tracks switch the three groups; the existing native finish
MPC animates paint. No runtime Python/C++ added. Python scripts are editor-only.
The first diagnostic render exposed stripes on wheel BPs; Keys_r01 is failed
visual evidence, not a deliverable. Do not rerun one-time prepare/resume scripts.

Preservation and reload
1257 protected files cover UE5.8, existing UE5.9 Config/Content, model sources,
and curated v11/itasha media. Verify protected_before.json before claiming intact.
Clear both original lookdev and itasha LVS packages before map reload, or restart.
tools/ue_v12_check.py performs the established safe reload and binding checks.
Runtime receiver checks concern rendered StaticMeshComponents; editor billboard
icons are excluded. There are 121 unique visible car meshes, 7 roof lines and
99,916 body-quad triangles; original world wake remains unattached.

Evidence and outputs
Reports: art/YU7_TUNNEL_FLOW/reports/itasha_v12
Media: renders/YU7_TunnelFlow/ItashaShowcase_v12
Raw frames are ignored reproducible intermediates in frames/.
See actual render status, decode validation, visual_review and output_manifest
for completion; authoring success alone does not establish final video quality.

Credits and limits
Retain CREDITS.txt verbatim and existing ART_SOURCES.txt beside the media.
Character source PNGs are unchanged official 1000px canvases; no character-art
reuse/distribution license was verified. Vehicle attribution does not cover them.
Finish colors are art-directed, not calibrated paint spectra. Roof curves are
illustrative, not CFD. Film remains silent. Packaged/new-machine validation and
application-visible Credits remain separate final-project delivery items.

Verified delivery: Final_r03_4K_24s.mp4 and Final_r03_4K_Labeled_24s.mp4,
Previs_r02_1080p_24s.mp4 and Previs_r02_1080p_Labeled_24s.mp4.
All four decode completely; both576-frame native renders visually reviewed.
Eleven curated4K PNGs are byte-identical to MRQ frames. Final safe reload,
Map Check0/0, real PIE13 states and1257 historical hashes pass.
