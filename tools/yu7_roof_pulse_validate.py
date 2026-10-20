"""Offline geometric check for the exact native WPO equations; no source writes."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports'
vs=[];fs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith('SM_YU7_'):continue
    b=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([[b+i for i in p.vertices] for p in o.data.polygons])
tree=BVHTree.FromPolygons(vs,fs);obj=bpy.data.objects['SM_RoofAirflow_v01']
def smooth(a,b,x):
    q=max(0.,min(1.,(x-a)/(b-a)));return q*q*(3-2*q)
def sn(x):return math.sin(math.tau*x)
def offset(p,l,t):
    env=smooth(.025,.12,p)*(1-smooth(.9,1.,p))*smooth(1.4,2.,t)
    a=(1.8*p-.28*t+.63*l)
    z=((5+17*smooth(.48,.84,p))*sn(a)+3*sn(3.4*p-.17*t-.81*l))*env
    y=(6+13*smooth(.45,.8,p))*sn(1.45*p-.23*t+.91*l)*env
    return y,z
minimum=(99,None);samples=0;max_offsets=[0,0];span=[[],[]]
for j in range(7):
    for k in range(0,1101,10):
        ring=[obj.data.vertices[j*1101*6+k*6+n].co for n in range(6)];base=sum(ring,Vector())/6;p=k/1100;l=j/6
        for frame in range(289):
            t=frame/24;dy,dz=offset(p,l,t);max_offsets=[max(max_offsets[0],abs(dy)),max(max_offsets[1],abs(dz))]
            if -2.49<base.x<2.49:
                y=base.y-dy*.01;z=base.z+dz*.01;hit=tree.ray_cast(Vector((base.x,y,4)),Vector((0,0,-1)),5)[0]
                if hit:
                    gap=z-hit.z-.003;samples+=1
                    if gap<minimum[0]:minimum=(gap,{'lane':j,'x':base.x,'time':t})
    for t in [4.,4.5]:span[int(t==4.5)].append(offset(.4,j/6,t))
assert minimum[0]>.04,minimum
result={'minimum_clearance_m':minimum[0],'worst_sample':minimum[1],'collision_samples':samples,'sample_rate_fps':24,'spatial_step_m':.1,'tube_radius_m':.003,'maximum_axis_offsets_cm':max_offsets,'roof_offsets_at_4s_and_4_5s_cm':span,'note':'Geometric samples of exact native WPO equations. Does not replace rendered-motion review.'}
(O/'roof_pulse_geometry_v08.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
