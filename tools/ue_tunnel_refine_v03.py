"""Visual refinement based on native v02 frames; only current TunnelFlow assets."""
import unreal,json
from pathlib import Path
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports';D='/Game/YU7/TunnelFlow'
E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mpc=unreal.load_asset(D+'/Materials/MPC_TunnelFlow')
code=(R/'tools/ue_tunnel_assets.py').read_text();code=code[code.index('class Graph:'):code.index('for name,color,rough')]
code=code.replace("        assert not E.does_asset_exist(D+'/Materials/'+name)\n        self.m=T.create_asset(name,D+'/Materials',unreal.Material,unreal.MaterialFactoryNew());self.n=0", "        assert name in ['M_TunnelGrid','M_TunnelSurfaceFlow','M_TunnelWorldWake']\n        self.m=unreal.load_asset(D+'/Materials/'+name);assert self.m\n        M.delete_all_material_expressions(self.m);self.n=0")
code=code.replace("'blend_mode':unreal.BlendMode.BLEND_ADDITIVE", "'blend_mode':unreal.BlendMode.BLEND_MASKED,'opacity_mask_clip_value':.008")
code=code.replace("g.out(1.,'OPACITY')", "g.out(energy,'OPACITY_MASK')")
code=code.replace('progress=g.div(g.sub(t,5.05),3.95)','progress=g.sat(g.div(g.sub(t,5.05),3.95))')
code=code.replace('peak=g.bell(d,.075)','peak=g.mul(g.bell(d,.09),g.inv(g.smooth(9.6,10.2,t)))')
code=code.replace('g.mul(lane,.22)','g.mul(g.inv(lane),.02)')
code=code.replace('default_value=210.','default_value=850.').replace('default_value=520.','default_value=2200.').replace('default_value=300.','default_value=900.')
exec(compile(code,'tunnel_material_v03','exec'))
m=unreal.load_asset(D+'/Materials/M_TunnelLane');n=M.get_material_property_input_node(m,unreal.MaterialProperty.MP_EMISSIVE_COLOR);n.set_editor_property('constant',unreal.LinearColor(20,22,23,1));M.recompile_material(m);E.save_loaded_asset(m)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'grid_brightness':850,'grid_afterglow':.15,'surface_brightness':2200,'wake_brightness':900,'rear_peak_hold':'9.0-9.6s; fade peak to 10.2s','flow_lane_fix':'Account for FBX V flip, phase variation only 0.02','note':'Based on v02 native frames, before full-length motion review.'}
(O/'refine_v03.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
