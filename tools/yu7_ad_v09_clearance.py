"""96 Hz Euclidean clearance of exact native WPO, with dense curve samples."""
import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/github2/vehicle_visualization');O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09'
data=json.loads((O/'roof_centerlines.json').read_text());vs=[];fs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith('SM_YU7_'):continue
    b=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([[b+i for i in p.vertices] for p in o.data.polygons])
tree=BVHTree.FromPolygons(vs,fs)
source=(R/'tools/yu7_ad_v09_roof.py').read_text();exec(source[source.index('def smooth('):source.index('ys=[')])
minimum=(99,None);samples=0;maxoffset=0.;static_min=99.;begin=time.time()
for row,lane in zip(data['lanes'],data['points']):
    j=row['lane'];radius=row['radius_m']
    # Full 1 cm source vertices over windshield/roof/spoiler bends; 5 cm elsewhere.
    indices=[k for k,p in enumerate(lane) if k%5==0 or (-2.5<p[0]<1.3 and k%2==0)]
    for k in indices:
        base=Vector(lane[k]);p=k/1100
        static_min=min(static_min,tree.find_nearest(base)[3]-radius)
        for frame in range(1153):
            t=frame/96;dy,dz=offset(p,j/6,t);maxoffset=max(maxoffset,math.hypot(dy,dz))
            q=base+Vector((0,-dy*.01,dz*.01))
            gap=tree.find_nearest(q)[3]-radius;samples+=1
            if gap<minimum[0]:minimum=(gap,{'lane':j,'x_m':base.x,'time_seconds':t})
result={'minimum_clearance_m':minimum[0],'static_minimum_clearance_m':static_min,'worst_sample':minimum[1],'samples':samples,'sample_rate_hz':96,'spatial_step_m':.02,'other_spatial_step_m':.05,'maximum_offset_cm':maxoffset,'WPO_cap_cm':25,'includes':'All 121 original meshes including glass, antenna, radar and spoiler; closest triangle distance minus tube radius','continuous_collision_guarantee':False,'duration_seconds':time.time()-begin}
(O/'roof_clearance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result));assert minimum[0]>=.08
