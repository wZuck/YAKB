"""Generate an engineering drawing from the same geometry as the CAD/PCB."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon
from common import ROOT, SPEC, keys

def main():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    fig=plt.figure(figsize=(16,11),facecolor='#f4f3ef');gs=fig.add_gridspec(3,1,height_ratios=[1.5,1.3,.7],hspace=.35)
    fig.suptitle('YAKB  /  Yet Another KeyBoard',x=.07,y=.975,ha='left',fontsize=24,fontweight='bold',color='#193f45')
    fig.text(.07,.935,'A0 engineering prototype • NiZ EC • 60 keys / 6u HHKB • BLE + USB • dimensions in mm',color='#566568')
    w,h=SPEC['pcb']['width'],SPEC['pcb']['height']
    ax=fig.add_subplot(gs[0]);ax.set_aspect('equal');ax.set_xlim(-12,w+12);ax.set_ylim(h+13,-13);ax.axis('off')
    ax.add_patch(FancyBboxPatch((-7,-7),w+14,h+14,boxstyle='round,pad=0,rounding_size=8',fc='#26484c',ec='none'))
    ax.add_patch(Rectangle((0,0),w,h,fc='#778b89',ec='none'))
    for k in keys():
        kw=k['width']*19.05-.8
        ax.add_patch(FancyBboxPatch((k['x']-kw/2,k['y']-9.125),kw,18.25,boxstyle='round,pad=0,rounding_size=1.2',fc='#faf9f4',ec='#c1c8c5',lw=.6))
        ax.text(k['x'],k['y']+.5,k['label'],ha='center',va='center',fontsize=7.2 if k['width']==1 else 8.5,color='#26484c')
    ax.add_patch(Rectangle((-.7,75.9),28.4,19.4,fc='#26484c'))
    ax.add_patch(Rectangle((238,75.9),47.7,19.4,fc='#26484c'))
    ax.text(263,86,'YAKB',color='#cad5ce',weight='bold',ha='center')
    ax.set_title('01  Fixed HHKB layout — asymmetric bottom row and centered-stem 6u spacebar',loc='left',pad=13,color='#193f45')
    ax=fig.add_subplot(gs[1]);ax.set_aspect('equal');ax.set_xlim(-10,w+10);ax.set_ylim(h+6,-8);ax.axis('off')
    ax.add_patch(Rectangle((0,0),w,h,fc='#e7ece5',ec='#436659'))
    for k in keys():ax.add_patch(Circle((k['x'],k['y']),7,ec='#8baca2',fc='none',lw=.7))
    bx,by,bz=SPEC['battery']['center'];bw,bh,bt=SPEC['battery']['bay']
    ax.add_patch(Rectangle((bx-bw/2,by-bh/2),bw,bh,ec='#b88836',fc='#f3dbac',lw=1.2))
    ax.text(bx,by,'Protected 1S LiPo\n60 × 35 × 5.5 max\n1000 mAh design budget',ha='center',va='center',fontsize=9,color='#704f23')
    ax.add_patch(Rectangle((243.25,76),33.5,18,fc='#315a72',alpha=.95));ax.text(260,85,'nice!nano v2',ha='center',va='center',color='white',fontsize=7)
    ax.add_patch(Rectangle((224,81),20,8,fc='#b7c0bd'));ax.text(227,70,'USB plug',fontsize=8)
    x0,y0,x1,y1=SPEC['module']['antenna_keepout'];ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,ec='#ce754e',lw=1.5,ls='--'))
    ax.annotate('RF copper keepout',xy=(277,82),xytext=(267,54),arrowprops={'arrowstyle':'-','color':'#a85836'},ha='right',color='#a85836',fontsize=8)
    from circuit import components
    for c in components():
        if c['ref'] in ['U2','U3','U4']:ax.add_patch(Rectangle((c['x']-3,c['y']-5),6,10,fc='#6b7778'));ax.text(c['x'],c['y']-8,c['ref'],ha='center',fontsize=7)
    for m in SPEC['mounts']:
        ax.add_patch(Rectangle((m['x']-m['width']/2,m['y']-m['height']/2),m['width'],m['height'],fill=False,ec='#ab5549',lw=1))
    ax.text(4,-3,'PCB 285.0 × 94.6 × 1.6',color='#436659',fontsize=9)
    ax.set_title('02  Shared plan view — underside modules, battery and Lot60-derived mounting clearances',loc='left',pad=13,color='#193f45')
    from matplotlib.transforms import Affine2D
    from generate_mechanical import floor_z,ANGLE
    ax=fig.add_subplot(gs[2]);ax.set_xlim(-12,110);ax.set_ylim(-18,17);ax.axis('off')
    for x,y,ww,hh,col in [(0,-1.6,h,1.6,'#467655'),(-5,6,h+10,1.6,'#8f9c9e'),(76,-8.1,18,6.5,'#315a72')]:ax.add_patch(Rectangle((x,y),ww,hh,fc=col))
    ax.add_patch(Polygon([(-7,floor_z(-7)),(h+7,floor_z(h+7)),(h+7,floor_z(h+7,True)),(-7,floor_z(-7,True))],fc='#26484c'))
    cell=Rectangle((5.5,-10.55),35,5.5,fc='#d6b475');cell.set_transform(Affine2D().rotate_deg_around(23,-7.8,ANGLE)+ax.transData);ax.add_patch(cell)
    ax.text(2,1,'PCB top z=0',fontsize=8);ax.text(2,9,'Plate z=6.0...7.6',fontsize=8)
    ax.text(12,-8,'tilted cell',fontsize=8);ax.text(77,-5,'module',fontsize=8,color='white')
    ax.text(0,-17,'Rear/front shell: 25.1 / 21.4 mm • 2.4 mm floor • 1.95 degree slope',fontsize=9,color='#566568')
    ax.set_title('03  Side envelope projection — rear at left / front at right; physical fit needs coupons',loc='left',pad=10,color='#193f45')
    fig.savefig(ROOT/'assets/design-overview.png',dpi=180,bbox_inches='tight',facecolor=fig.get_facecolor())
    plt.close(fig)

if __name__=='__main__':main()
