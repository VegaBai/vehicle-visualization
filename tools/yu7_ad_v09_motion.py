"""Pure offline authoring math, baked to native Sequencer; not a runtime module."""
import math
def curve(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    if t>=keys[-1][0]:return keys[-1][1]
    h=[b[0]-a[0] for a,b in zip(keys,keys[1:])]
    d=[(b[1]-a[1])/v for a,b,v in zip(keys,keys[1:],h)]
    m=[d[0]]
    for i in range(1,len(keys)-1):
        if d[i-1]*d[i]<=0:m.append(0.)
        else:
            w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1];m.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
    m.append(d[-1])
    i=next(i for i in range(len(keys)-1) if keys[i][0]<=t<=keys[i+1][0]);u=(t-keys[i][0])/h[i]
    return (2*u**3-3*u*u+1)*keys[i][1]+(u**3-2*u*u+u)*h[i]*m[i]+(-2*u**3+3*u*u)*keys[i+1][1]+(u**3-u*u)*h[i]*m[i+1]
ANGLE=[(0,35),(4.5,50),(8.5,76),(9,82),(9.5,84),(11,104),(12,112)]
RADIUS=[(0,890),(4.5,785),(8.5,805),(9,825),(9.5,825),(11,880),(12,900)]
HEIGHT=[(0,110),(4.5,125),(8.5,135),(9,135),(9.5,135),(11,125),(12,125)]
def camera_at(t):
    a=math.radians(curve(t,ANGLE));r=curve(t,RADIUS);z=curve(t,HEIGHT)
    x=-r*math.cos(a);y=r*math.sin(a)
    return (-1500*t+x,y,z),(math.degrees(math.atan2(77-z,r)),math.degrees(math.atan2(-y,-x)),0.)
def smooth(a,b,x):
    q=max(0.,min(1.,(x-a)/(b-a)));return q*q*(3-2*q)
def body_head(t):return max(0.,min(1.,(t-114/24)/(90/24)))
