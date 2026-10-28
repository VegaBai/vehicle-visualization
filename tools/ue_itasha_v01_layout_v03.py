"""Correct decal UV U=local Z / V=local Y orientation and corresponding extents."""
import unreal,json
from pathlib import Path
D='/Game/YU7/Itasha_v01';O=Path('C:/github2/vehicle_visualization/art/YU7_ITASHA/reports/v01')
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);E=unreal.EditorAssetLibrary;V=unreal.VariantManagerLibrary
assert not unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering()
actors={a.get_actor_label():a for a in A.get_all_level_actors()};manager=actors['YU7_ItashaOptions'];lvs=manager.get_level_variant_sets(True);s=lvs.get_variant_set_by_name('Itasha')
ratios={'None':882/782,'Rengoku':882/782,'Zenitsu':505/566,'Giyu':776/558}
for name,ratio in ratios.items():
    variant=s.get_variant_by_name(name)
    for side in ['Left','Right','Hood']:
        a=actors['YU7_Itasha_'+side];c=a.get_component_by_class(unreal.DecalComponent)
        if side=='Hood':
            c.set_editor_property('decal_size',unreal.Vector(30,45,55));scale=unreal.Vector(1,110/ratio/90,1)
        else:
            a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=-90 if side=='Left' else 90,roll=-90),True)
            c.set_editor_property('decal_size',unreal.Vector(25,43,90));scale=unreal.Vector(1,84/86,84*ratio/180)
        c.set_editor_property('relative_scale3d',scale)
        capture=next(p for p in V.get_captured_properties(variant,a) if p.get_full_display_string()=='Decal Component / Relative Scale 3D')
        capture.record()
for side,yaw in [('Left',-90),('Right',90)]:
    a=actors['YU7_Itasha_Sweep_'+side];a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=-90),True)
    a.get_component_by_class(unreal.DecalComponent).set_editor_property('decal_size',unreal.Vector(26,34,185))
assert manager.switch_on_variant_by_name('Itasha','Rengoku');E.save_loaded_asset(lvs);assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
RESULT={'layout':'v03','side_roll':-90,'art_height_cm':84,'hood_width_cm':110,'ratios':ratios,'status':'visual verification pending'}
(O/'layout_v03.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
