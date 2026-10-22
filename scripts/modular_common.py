"""Shared B1 flex centreline and exact tapered outline (PCB construction frame)."""
import json
from common import ROOT
D=json.loads((ROOT/'design/modular.json').read_text())
def bez(t):
 p=D['flex']['controls'];u=1-t
 return tuple(u**3*p[0][k]+3*u*u*t*p[1][k]+3*u*t*t*p[2][k]+t**3*p[3][k] for k in [0,1])
def flex_geometry():
 points=[tuple(D['flex']['contacts'][0])]+[bez(i/100) for i in range(101)]+[tuple(D['flex']['contacts'][1])]
 # 24 mm mating tabs, 26 mm body: widening restores edge clearance on the diagonal.
 widths=[12+max(0,min(1,(i/100-.04)/.12,(.96-i/100)/.12)) for i in range(101)]
 widths=[12]+widths+[12]
 path=[(points[0][0],points[0][1]-3)]+points+[(points[-1][0],points[-1][1]+3)]
 widths=[12]+widths+[12]
 poly=[(x-w,y) for (x,y),w in zip(path,widths)]+[(x+w,y) for (x,y),w in reversed(list(zip(path,widths)))]
 return points,poly
