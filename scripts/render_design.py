"""Publication-scale vector drawings from delivered DXF, STEP and routed PCB."""
import json
import cadquery as cq
import ezdxf
from ezdxf.path import make_path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Circle
from matplotlib.collections import PolyCollection
from common import ROOT,SPEC
from render_provenance import hashes, record
from render_plan import draw_board,PAPER,INK

def project_section(ax,name,x,color):
    shape=cq.importers.importStep(str(ROOT/'mechanical'/(name+'.step'))).val().mirror('XZ')
    slab=cq.Workplane('XY').box(.1,180,100).translate((x,45,0)).val();cut=shape.intersect(slab)
    if cut.isNull():return
    vv,ff=cut.tessellate(.03,.07)
    ax.add_collection(PolyCollection([[(vv[i].y,vv[i].z) for i in f] for f in ff],facecolors=color,edgecolors='none'))

def dimension(ax,a,b,y,text):
    ax.plot([a,a],[y-1,y+2],color=INK,lw=.6);ax.plot([b,b],[y-1,y+2],color=INK,lw=.6)
    ax.annotate('',(a,y),(b,y),arrowprops=dict(arrowstyle='<->',color=INK,lw=.65));ax.text((a+b)/2,y-1.8,text,ha='center',va='bottom',fontsize=8,color=INK,bbox=dict(fc=PAPER,ec='none',pad=1))

def main():
    sources=hashes(['hardware/YAKB.kicad_pcb','design/pad-map.json','design/pcb-scene.json','mechanical/plate_case.dxf','reports/mechanical.json','scripts/render_design.py','scripts/render_plan.py']+[f'mechanical/{n}.step' for n in ['case_base','case_bezel','plate_case','pcb_envelope','battery_envelope']])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
    fig=plt.figure(figsize=(17,13),facecolor=PAPER);gs=fig.add_gridspec(3,1,height_ratios=[1,1,.46],left=.055,right=.945,top=.87,bottom=.06,hspace=.40)
    fig.text(.055,.95,'YAKB',fontsize=33,weight='bold',color=INK);fig.text(.945,.953,'YET ANOTHER KEYBOARD / A0',ha='right',fontsize=10,color=INK)
    fig.text(.055,.913,'GEOMETRY ATLAS  /  NiZ electrocapacitive  /  fixed 60-key HHKB  /  dimensions in mm',fontsize=11,color='#647368')
    ax=fig.add_subplot(gs[0]);ax.set_aspect('equal');ax.axis('off');ax.set_xlim(-12,297);ax.set_ylim(108,-16)
    d=ezdxf.readfile(ROOT/'mechanical/plate_case.dxf')
    segments=[[(v.x,-v.y) for v in make_path(e).flattening(.01)] for e in d.modelspace() if e.dxf.layer=='CUT']
    loops=[]
    near=lambda a,b:sum((x-y)**2 for x,y in zip(a,b))<1e-8
    while segments:
        loop=segments.pop()
        while not near(loop[0],loop[-1]):
            hit=next(((i,False) for i,a in enumerate(segments) if near(a[0],loop[-1])),None)
            if hit is None:hit=next(((i,True) for i,a in enumerate(segments) if near(a[-1],loop[-1])),None)
            assert hit is not None,'DXF contour is not closed'
            i,reverse=hit;part=segments.pop(i);loop.extend((part[::-1] if reverse else part)[1:])
        loops.append(loop)
    area=lambda a:abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(a,a[1:])))
    for i,loop in enumerate(sorted(loops,key=area,reverse=True)):
        ax.add_patch(Polygon(loop,fc='#809185' if i==0 else PAPER,ec=INK,lw=.45))
    dimension(ax,-5,290,-10,'295.00')
    ax.set_title('01 / MACHINING PROFILE     Actual plate_case.dxf cut contours, including stabilizer latches',loc='left',fontsize=10,color=INK,pad=17)
    ax=fig.add_subplot(gs[1]);draw_board(ax,front=False)
    ax.set_title('02 / ROUTED PCB BACK     285.0 x 94.6 x 1.6 mm / true copper polygons / already mirrored',loc='left',fontsize=10,color=INK,pad=14)
    ax=fig.add_subplot(gs[2]);ax.set_xlim(-12,110);ax.set_ylim(-18,14);ax.set_aspect('equal');ax.axis('off')
    for name,color in [('case_base','#365647'),('case_bezel','#365647'),('plate_case','#829084'),('pcb_envelope','#398267'),('battery_envelope','#b39b69')]:project_section(ax,name,142.5,color)
    ax.axhline(0,color='#9fada0',lw=.55,ls=(0,(4,4)));ax.text(106,1,'PCB top z=0',ha='right',fontsize=8,color=INK)
    profile=json.loads((ROOT/'reports/mechanical.json').read_text())['case_profile']
    ax.set_title(f"03 / CENTER SECTION     x=142.5 / rear to front / {profile['typing_angle_deg']:.3f} degree floor",loc='left',fontsize=10,color=INK,pad=11)
    fig.text(.055,.022,'Contours and sections are exported geometry. Actual NiZ, stabilizer, battery and cable samples remain mandatory.',fontsize=8,color='#647368')
    for suffix in ['png','svg']:fig.savefig(ROOT/'assets'/('design-overview.'+suffix),dpi=210,facecolor=PAPER)
    from common import normalize_text
    normalize_text(ROOT/'assets/design-overview.svg')
    plt.close(fig)
    record('assets/plan-render-manifest.json',sources,['assets/design-overview.png','assets/design-overview.svg'],'Matplotlib vector DXF / native PCB / STEP section')

if __name__=='__main__':main()
