"""Vector technical views using native KiCad polygons, copper and board edges."""
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib.patches import Polygon, Circle, FancyBboxPatch
from matplotlib.collections import LineCollection
from common import ROOT

PAPER='#f1f0e9'
INK='#173a36'

def draw_board(ax, front=False, selected=None):
    scene=json.loads((ROOT/'design/pcb-scene.json').read_text())
    parts=json.loads((ROOT/'design/pad-map.json').read_text())
    # Outer board vertices are exported in order, including its open side slots.
    edges=scene['edges']; outer=[]
    # PCB_SHAPE iteration is stable but not contour-sorted: connect nearest ends.
    remain=list(edges); first=min(range(len(remain)),key=lambda i:min(p[1] for p in remain[i]));edge=remain.pop(first);outer.extend(edge)
    while remain:
        hit=next(((i,False) for i,e in enumerate(remain) if sum((a-b)**2 for a,b in zip(e[0],outer[-1]))<1e-9),None)
        if hit is None:hit=next(((i,True) for i,e in enumerate(remain) if sum((a-b)**2 for a,b in zip(e[1],outer[-1]))<1e-9),None)
        if hit is None:break
        i,reverse=hit;e=remain.pop(i);outer.append(e[0] if reverse else e[1])
    ax.add_patch(Polygon(outer,fc='#214c40',ec='#112e28',lw=.7,zorder=1))
    layer='F.Cu' if front else 'B.Cu'
    for t in scene['tracks']:
        if t.get('via'):
            ax.add_patch(Circle(t['at'],t['width']/2,fc='#36715b',ec='none',zorder=2))
            ax.add_patch(Circle(t['at'],t['drill']/2,fc='#142e28',ec='none',zorder=3))
        elif t['layer']==layer:
            # widths are in data units; a polygon is independent of output dpi.
            import math
            a,b=t['a'],t['b'];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
            if not length:continue
            nx,ny=-dy/length*t['width']/2,dx/length*t['width']/2
            ax.add_patch(Polygon([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)],fc='#3c765d',ec='none',zorder=2))
    for part in parts:
        active=selected is not None and part['ref'] in selected
        for pad in part['pads']:
            mask=pad['front_mask'] if front else pad['back_mask']
            col=('#e4bb70' if mask else '#43836b') if selected is None or active else ('#798975' if mask else '#326450')
            for poly in pad['front_polygons' if front else 'back_polygons']:
                ax.add_patch(Polygon(poly,fc=col,ec='none',zorder=4))
            if pad['through']:
                dx,dy=pad['drill'];ax.add_patch(Circle((pad['x'],pad['y']),dx/2,fc='#142e28',ec='none',zorder=5))
            if active and pad['number']=='1':ax.add_patch(Circle((pad['x'],pad['y']),max(pad['width'],pad['height'])/2+.36,fill=False,ec='#fff5d4',lw=.8,zorder=6))
        if active:
            ax.annotate(part['ref'],(part['x'],part['y']),xytext=(0,20),textcoords='offset points',ha='center',fontsize=8,
                        color=INK,weight='bold',bbox=dict(boxstyle='round,pad=.28',fc=PAPER,ec='none'),zorder=8,
                        arrowprops=dict(arrowstyle='-',lw=.7,color='#d2e0cc'))
    # Other edge loops, such as the large lower-left aperture.
    if remain:
        from matplotlib.path import Path
        # closed loops are connected independently, so no assumed rectangles.
        while remain:
            e=remain.pop(0);loop=list(e)
            while True:
                hit=next(((i,False) for i,a in enumerate(remain) if sum((x-y)**2 for x,y in zip(a[0],loop[-1]))<1e-9),None)
                if hit is None:hit=next(((i,True) for i,a in enumerate(remain) if sum((x-y)**2 for x,y in zip(a[1],loop[-1]))<1e-9),None)
                if hit is None:break
                i,reverse=hit;a=remain.pop(i);loop.append(a[0] if reverse else a[1])
            ax.add_patch(Polygon(loop,fc=PAPER,ec='#112e28',lw=.6,zorder=7))
    for hole in scene['holes']:
        x,y=hole['at'];w,h=hole['size']
        ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle=f'round,pad=0,rounding_size={min(w,h)/2}',fc=PAPER,ec='#112e28',lw=.5,zorder=7))
    ax.set_aspect('equal');ax.axis('off')
    ax.set_xlim((-5,290) if front else (290,-5));ax.set_ylim(100,-5)
    return parts
