"""Authoring values; no runtime Python dependency."""
from pathlib import Path
R=Path('C:/github2/vehicle_visualization')
O=R/'art/YU7_TUNNEL_FLOW/reports/finish_v11'
D='/Game/YU7/TunnelFlow/FinishShowcase_v11'
MAP=D+'/Maps/Studio_YU7_FinishShowcase_v11'
SEQ=D+'/Sequences/LS_YU7_FinishShowcase_v11_18s'
TOTAL=432
FINISHES=[
    dict(name='Grey Blue | Gloss Wrap',frame=0,PigmentColor=[.18,.27,.34],EdgeTint=[.24,.32,.38],Metallic=.04,BaseRoughness=.23,ClearCoat=1.,CoatRoughness=.045,Specular=.5,ColorFlop=.10,FlakeStrength=0.),
    dict(name='Ice Blue | Metallic Paint',frame=30,PigmentColor=[.12,.23,.32],EdgeTint=[.29,.40,.49],Metallic=.78,BaseRoughness=.24,ClearCoat=1.,CoatRoughness=.085,Specular=.5,ColorFlop=.42,FlakeStrength=.09),
    dict(name='Opal White | Pearlescent Paint',frame=60,PigmentColor=[.55,.57,.59],EdgeTint=[.40,.47,.64],Metallic=.20,BaseRoughness=.29,ClearCoat=1.,CoatRoughness=.09,Specular=.5,ColorFlop=.72,FlakeStrength=.035),
    dict(name='Graphite Grey | Matte Wrap',frame=90,PigmentColor=[.095,.115,.13],EdgeTint=[.15,.17,.18],Metallic=.03,BaseRoughness=.62,ClearCoat=.03,CoatRoughness=.48,Specular=.35,ColorFlop=.12,FlakeStrength=0.),
    dict(name='Porcelain Grey | Ceramic Gloss',frame=120,PigmentColor=[.24,.255,.27],EdgeTint=[.29,.305,.32],Metallic=.02,BaseRoughness=.20,ClearCoat=1.,CoatRoughness=.028,Specular=.5,ColorFlop=.08,FlakeStrength=0.),
    dict(name='Mineral Teal | Original Finish',frame=156),
]

def source_frame(f):
    # 7x slower first six seconds, C1/C2-smooth acceleration over two seconds.
    # At output frame192 the v10 source is frame48; remainder keeps original speed.
    if f<=144:return f/7
    if f>=192:return f-144
    x=f-144
    return 144/7+x/7+(6/7)*(x**3/48**2-x**4/(2*48**3))
