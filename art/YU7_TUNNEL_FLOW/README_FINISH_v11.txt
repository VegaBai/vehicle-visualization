YU7 MATERIAL IN MOTION — FINISH SHOWCASE v11
2026-10-21

Request and scope
Show different paint and wrap finishes in the opening, including metallic,
pearlescent, matte, gloss, and the supplied grey-blue / grey ceramic-gloss look.
The user explicitly selected approximately 18 seconds instead of the old 12.
Source reference: references/finish_v11/user_grey_blue_gloss.png (user supplied).

Isolated editable assets
/Game/YU7/TunnelFlow/FinishShowcase_v11/Maps/Studio_YU7_FinishShowcase_v11
/Game/YU7/TunnelFlow/FinishShowcase_v11/Sequences/LS_YU7_FinishShowcase_v11_18s
/Game/YU7/TunnelFlow/FinishShowcase_v11/Materials/M_YU7_Finish_v11
/Game/YU7/TunnelFlow/FinishShowcase_v11/Materials/MPC_YU7_Finish_v11
Reports: reports/finish_v11
Media: renders/YU7_TunnelFlow/FinishShowcase_v11 (repository root)

Finish timeline (24 fps)
0–24: grey-blue gloss wrap; 24–30 transition.
30–54: blue metallic paint; 54–60 transition.
60–84: opal-white pearlescent paint; 84–90 transition.
90–114: graphite-grey matte wrap; 114–120 transition.
120–150: porcelain-grey ceramic gloss; 150–156 transition.
156 onward: original mineral-teal values, with the existing flow / quad shot.
Transitions use six-frame eased parameter changes, not full-frame dissolves.
Nine visible paint slots change together; glass, lights, tyres and trim retain
their original materials. Exact parameter values are in reports/finish_v11/palette.json.

Native implementation
All runtime work remains native Blueprint actors, Sequencer and material nodes.
A new MPC animates pigment, edge colour, metallic, base roughness, clear coat,
coat roughness, specular, colour flop and subtle UV-stable microflake modulation.
Python only prepares/checks editor assets; FFmpeg encodes the offline deliverables.
These are art-directed finish representations, not calibrated manufacturer paint
codes or measured coating/pearlescent spectra. Fine flakes are subtle in this
whole-car medium shot; do not claim a macro flake demonstration.

Motion retiming
432 frames / 18 seconds. First six seconds run the original camera, car and wheel
motion at 1/7 speed. A smooth acceleration over seconds 6–8 reaches the old source
time 2s at new 8s. Thereafter source time = output time - 6s. ShotTime and following
lights are retimed with the same function, so airflow/grid phases follow the car.
Original v10 roof geometry, WPO, camera path, lighting and effect materials are
shared unchanged. Original 121 unique visible vehicle meshes, full 99,916-triangle
quad body and unattached world wake are preserved. Reference v10 sampled clearance
is historical evidence; this task does not claim a new physical airflow solution.

Verification status
Saved-map/LVS-cache-clear/reload audit passed, native finish values were evaluated
at all six plateau starts, and 708 protected historical file hashes matched.
Keyframes_r02_1080p: nine native frames completed (54.86s, success, no errors).
Previs_r03_1080p: 432 native frames completed (229.96s, success, no MRQ errors).
Final_r04_4K: 432 native 3840x2160 frames, 8 temporal samples, completed in
1469.00s (success, no MRQ errors). All 18 contact sheets for each full sequence
and nine final 4K keyframes were actually viewed. Five finishes, teal return,
continuous retimed motion, full rear-door quad and clean final 24 frames passed.
All PNGs and all four encoded MP4s passed complete decoding at 24 fps / 18 seconds.
The five bilingual labels and their exit were checked from decoded video frames.
Final safe reload audit passed; Map Check reported 0 Errors / 0 Warnings, no dirty
packages, 708 protected hashes unchanged. See scene_audit.json, final_mapcheck.log,
visual_review.json, *_validation.json and output_manifest.json for evidence.
Lumen automatically increased ScreenProbeGather DownsampleFactor from 4 to 8 to
fit the maximum texture size during 4K rendering; output remains native 4K.
No realtime player viewing or human aesthetic acceptance is claimed.

Completed deliverables (under renders/YU7_TunnelFlow/FinishShowcase_v11)
Final_r04_4K_Labeled_18s.mp4 — default presentation, five opening finish names.
Final_r04_4K_18s.mp4 — native rendered frames without editorial text.
Previs_r03_1080p_Labeled_18s.mp4 and Previs_r03_1080p_18s.mp4 — smaller previews.
01–09_*_v11_4K.png — nine unaltered native final frames.
Final_r04_4K_FinishComparison.jpg — review comparison derived from six frames.
CREDITS.txt — byte-identical attribution sidecar; exact text also in MP4 metadata.
Output manifest records 4 videos, 9 stills, 24 native assets and all file SHA256 values.
Complete raw PNG sequences are reproducible ignored local intermediates.

Recovery and reuse
Do not rerun one-time prepare/resume/sequence scripts over these existing assets.
The first generic map duplicate left an unsaved standalone world and triggered
UE world-cleanup failure. Targeted recovery used the established save_map workflow.
Noise's actual editor input is named World Position, though supplied coordinates
are stable mesh UVs. The unfinished material alone was rebuilt after that discovery.
An initial MRQ setup crashed in Python before any output; restarting directly in
the saved v11 map allowed native rendering. Exact root cause is not established.
Preserve failures/logs and r01 presets as process evidence. Use fresh output names.
Keep the established LVS cache-clear-before-map-reload rule, or restart the editor.

Credits and final-project limits
Preserve root CREDITS.txt verbatim in delivery sidecars and video/sequence metadata.
Visible application Credits UI and packaged/new-machine testing remain separate
final-project delivery items. This shot remains silent.
