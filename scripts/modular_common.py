"""Shared physical FPC outline, including rounded mating ears and straight stiffened tabs."""
import json,math
from common import ROOT
D=json.loads((ROOT/'design/modular.json').read_text());I=json.loads((ROOT/'design/fpc-interface.json').read_text())
def bez(t):
 p=D['flex']['controls'];u=1-t
 return tuple(u**3*p[0][k]+3*u*u*t*p[1][k]+3*u*t*t*p[2][k]+t**3*p[3][k] for k in [0,1])
def rounded_polygon(vertices):
 out=[]
 for i,(x,y,r) in enumerate(vertices):
  prev=vertices[i-1];nxt=vertices[(i+1)%len(vertices)];u=(prev[0]-x,prev[1]-y);v=(nxt[0]-x,nxt[1]-y);a=math.hypot(*u);b=math.hypot(*v);u=(u[0]/a,u[1]/a);v=(v[0]/b,v[1]/b);theta=math.acos(max(-1,min(1,u[0]*v[0]+u[1]*v[1])))
  if not r or abs(math.pi-theta)<1e-6:out.append((x,y));continue
  t=min(r/math.tan(theta/2),a*.4,b*.4);r=t*math.tan(theta/2);bis=(u[0]+v[0],u[1]+v[1]);bl=math.hypot(*bis);dist=r/math.sin(theta/2);c=(x+bis[0]/bl*dist,y+bis[1]/bl*dist);p=(x+u[0]*t,y+u[1]*t);q=(x+v[0]*t,y+v[1]*t);ang=math.atan2(p[1]-c[1],p[0]-c[0]);end=math.atan2(q[1]-c[1],q[0]-c[0]);sweep=(end-ang+math.pi)%(2*math.pi)-math.pi
  count=max(3,math.ceil(abs(sweep)/.12))
  out.extend((c[0]+r*math.cos(ang+sweep*j/count),c[1]+r*math.sin(ang+sweep*j/count)) for j in range(count+1))
 return out

def outline_from_curve(points,curve,widths):
 tips=[(points[0][0],points[0][1]-I['finger_length_mm']/2),(points[-1][0],points[-1][1]+I['finger_length_mm']/2)]
 def side(tip,sign,left):
  x,y=tip;w=I['terminal_width_mm']/2;s=-1 if left else 1
  return [(x+s*w,y,.3),(x+s*w,y+sign*1.1,.1),(x+s*(w+.55),y+sign*1.5,.1),(x+s*(w+.55),y+sign*2.2,.1),(x+s*w,y+sign*2.2,.1),(x+s*w,y+sign*5,0)]
 left=side(tips[0],1,True)+[(x-w,y,0) for (x,y),w in zip(curve,widths)]+list(reversed(side(tips[1],-1,True)))
 right=side(tips[0],1,False)+[(x+w,y,0) for (x,y),w in zip(curve,widths)]+list(reversed(side(tips[1],-1,False)))
 return rounded_polygon(left+list(reversed(right)))

def flex_geometry(coupon=False):
 if coupon:
  curve=[(0,5.5),(0,I['coupon_tip_distance_mm']-5.5)];points=[(0,1.75)]+curve+[(0,I['coupon_tip_distance_mm']-1.75)];widths=[12.5,12.5]
 else:
  curve=[bez(i/100) for i in range(101)];points=[tuple(D['flex']['contacts'][0])]+curve+[tuple(D['flex']['contacts'][1])]
  widths=[12.5+.5*max(0,min(1,(i/100-.04)/.12,(.96-i/100)/.12)) for i in range(101)]
 return points,outline_from_curve(points,curve,widths)

def clip_y(poly,low,high):
 """Clip the real outline to a stiffener interval; preserves ear/tip geometry."""
 points=list(poly)
 for limit,above in [(low,True),(high,False)]:
  out=[]
  for a,b in zip(points,points[1:]+points[:1]):
   ia=a[1]>=limit-1e-10 if above else a[1]<=limit+1e-10;ib=b[1]>=limit-1e-10 if above else b[1]<=limit+1e-10
   if ia:out.append(a)
   if ia!=ib:
    t=(limit-a[1])/(b[1]-a[1]);out.append((a[0]+t*(b[0]-a[0]),limit))
  points=out
 return points
