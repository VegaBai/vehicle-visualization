"""Read-only distance sampling of prepared line ring centres and span interiors."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('C:/github2/vehicle_visualization');VERSION=globals().get('VERSION','v03')
vv=[];ff=[]
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('SM_YU7_'):
        base=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices)
        ff.extend([[base+i for i in p.vertices] for p in o.data.polygons])
tree=BVHTree.FromPolygons(vv,ff);dist=[];centres=0;interiors=0
for o in bpy.data.collections['YU7_BODY_QUAD_'+VERSION].objects:
    m=o.data;cc=[sum((m.vertices[i+q].co for q in range(6)),Vector())/6 for i in range(0,len(m.vertices),6)];centres+=len(cc)
    for c in cc:dist.append(tree.find_nearest(c)[3])
    pairs={tuple(sorted(set(i//6 for i in f.vertices))) for f in m.polygons if len(f.vertices)==4}
    for pair in pairs:
        if len(pair)!=2:continue
        for t in [.25,.5,.75]:
            dist.append(tree.find_nearest(cc[pair[0]].lerp(cc[pair[1]],t))[3]);interiors+=1
result={'version':VERSION,'line_centres':centres,'span_interior_samples':interiors,'nearest_source_surface_distance_m':{'min':min(dist),'max':max(dist),'mean':sum(dist)/len(dist)},'scope':'Distance to nearest source triangle at line centres and span quarter points, not CAD certification.'}
(ROOT/'art/YU7_QUAD_BODY/reports'/('geometry_fit_'+VERSION+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
assert max(dist)<.00161,result
print(json.dumps(result))
