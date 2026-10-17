"""Generate an original analytic softbox diffuser; no external image input."""
import math,struct,zlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'art/YU7_UNREAL/Lookdev';out.mkdir(exist_ok=True)
w,h=512,256
def smooth(x):
    x=max(0.,min(1.,x));return x*x*(3.-2.*x)
raw=bytearray()
for y in range(h):
    raw.append(0)
    v=(y+.5)/h
    for x in range(w):
        u=(x+.5)/w
        edge=smooth(min(u,1-u)/.16)*smooth(min(v,1-v)/.24)
        gradient=.25+.75*math.sin(math.pi*v)**.7
        n=round(255*edge*gradient)
        raw.extend([n,n,n])
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
(out/'T_SoftboxDiffuser.png').write_bytes(png)
print(str(out/'T_SoftboxDiffuser.png'))
