"""Use depth-tested masked unlit display after additive failed native MRQ visibility."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mpc=unreal.load_asset(D+'/Materials/MPC_TunnelFlow')
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('class Graph:'):code.index('for name,color,rough')]
code=code.replace("        assert not E.does_asset_exist(D+'/Materials/'+name)\n        self.m=T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());self.n=0", "        assert name in ['M_TunnelGrid','M_TunnelSurfaceFlow','M_TunnelWorldWake']\n        self.m=unreal.load_asset(D+'/Materials/'+name);assert self.m\n        M.delete_all_material_expressions(self.m);self.n=0")
code=code.replace("'blend_mode':unreal.BlendMode.BLEND_ADDITIVE", "'blend_mode':unreal.BlendMode.BLEND_MASKED,'opacity_mask_clip_value':.008")
code=code.replace("g.out(1.,'OPACITY')", "g.out(energy,'OPACITY_MASK')")
exec(compile(code,'native_masked_materials','exec'))
actors={a.get_actor_label():a for a in A.get_all_level_actors()}
for label in ['Body','Mirror_L','Mirror_R']:actors['YU7_BodyQuad_'+label].static_mesh_component.set_material(0,unreal.load_asset(D+'/Materials/M_TunnelGrid'))
actors['YU7_Tunnel_SurfaceFlow'].static_mesh_component.set_material(0,unreal.load_asset(D+'/Materials/M_TunnelSurfaceFlow'))
seq=unreal.load_asset(D+'/Sequences/LS_YU7_TunnelFlow_12s')
for b in seq.get_bindings():
    for tr in b.get_tracks():
        if isinstance(tr,unreal.MovieSceneFloatTrack) and str(tr.get_property_name())=='Intensity':
            for s in tr.get_sections():
                for c in s.get_all_channels():
                    for k in c.get_keys():k.set_value(k.get_value()*.22)
E.save_loaded_asset(seq);unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'materials':'Three native unlit masked graphs; energy drives opacity mask, clip=.008; inactive area discarded','debug_materials_unassigned':True,'scan_light_factor':.22}
(O/'masked_refine.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
