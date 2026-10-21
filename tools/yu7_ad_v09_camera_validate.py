"""Validate camera interpolated keys against every actual visible environment box."""
import math,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'art/YU7_TUNNEL_FLOW/reports/art_direction_v09'
exec(compile((R/'tools/yu7_ad_v09_motion.py').read_text(),'motion_math','exec'))
boxes=json.loads((O/'environment_boxes.json').read_text());centers=np.array([b['center'] for b in boxes]);axes=np.array([b['axes'] for b in boxes]);scales=np.linalg.norm(axes,axis=2);units=axes/scales[:,:,None];extents=np.array([b['half'] for b in boxes])*scales
minimum=(1e10,None);intersections=[];angles=[];samples=[]
for f in range(1153):
    t=f/96;frame=t*24;lo=math.floor(frame);alpha=frame-lo
    # Native channel keys are linear between display frames.
    cam=(1-alpha)*np.array(camera_at(lo/24)[0])+alpha*np.array(camera_at((lo+1)/24)[0]);local=np.einsum('bi,bji->bj',cam-centers,units)
    distance=np.linalg.norm(np.maximum(np.abs(local)-extents,0),axis=1);i=int(distance.argmin())
    if distance[i]<minimum[0]:minimum=(float(distance[i]),{'time':t,'component':boxes[i]['component'],'instance':boxes[i]['instance']})
    target=np.array([-1500*t,0,77]);direction=np.einsum('i,bji->bj',target-cam,units)
    safe=np.where(np.abs(direction)<1e-12,1e-12,direction)
    a=(-extents-local)/safe;b=(extents-local)/safe
    enter=np.max(np.minimum(a,b),axis=1);leave=np.min(np.maximum(a,b),axis=1)
    hits=np.flatnonzero((enter<=leave)&(leave>0)&(enter<1))
    for i in hits:intersections.append({'time':t,'component':boxes[int(i)]['component'],'instance':boxes[int(i)]['instance']})
    angles.append(curve(t,ANGLE));samples.append(float(cam[1]))
result={'sample_rate_hz':96,'samples':1153,'actual_visible_instance_boxes':len(boxes),'minimum_camera_to_geometry_cm':minimum[0],'worst_sample':minimum[1],'line_of_sight_intersections':intersections,'max_world_y_cm':max(samples),'angle_monotonic':all(a<=b for a,b in zip(angles,angles[1:])),'near_clip_clearance_target_cm':50,'method':'Oriented native mesh bounding boxes, exact linearly interpolated camera key positions; center sightline slab intersection. Rendering still required.'}
(O/'camera_clearance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2));assert minimum[0]>=50 and not intersections
