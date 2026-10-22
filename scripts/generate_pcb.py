"""Run with KiCad's Python (pcbnew). Produces an UNROUTED design board."""
import json, math, csv
import pcbnew as p
import wx
from common import ROOT, SPEC
from circuit import components

OUT=ROOT/"hardware"
LIB="/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
def v(x,y): return p.VECTOR2I(round(x*1e6),round(y*1e6))
def hole_layers():
    # AllCuMask() is a reference to KiCad's shared static mask. Mutating it
    # corrupts serialization of *.Cu and silently loses soldermask on reload.
    ls=p.LSET(p.LSET.AllCuMask());ls.AddLayer(p.F_Mask);ls.AddLayer(p.B_Mask);return ls

def simple_footprint(name, pins):
    f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID("YAKB",name))
    for num,x,y in pins:
        a=p.PAD(f);a.SetNumber(str(num));a.SetPosition(v(x,y));a.SetSize(v(1.8,1.8));a.SetDrillSize(v(1,1));a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetAttribute(p.PAD_ATTRIB_PTH);a.SetLayerSet(hole_layers());f.Add(a)
    return f

def main():
    app=wx.App(False)
    for name,pins in [("SPST_PIGTAIL_2.54",[(1,-1.27,0),(2,1.27,0)]),("RESET_2.54_TH",[(1,-1.27,0),(2,1.27,0)])]:
        p.FootprintSave(str(OUT/"YAKB.pretty"),simple_footprint(name,pins))
    b=p.BOARD();b.GetDesignSettings().SetBoardThickness(p.FromMM(SPEC["pcb"]["thickness"]))
    b.SetCopperLayerCount(4)
    cs=components(); nets={}
    for name in sorted({n for c in cs for n in c["pins"].values() if n}):
        a=p.NETINFO_ITEM(b,name);b.Add(a);nets[name]=a
    for c in cs:
        lib,name=c["footprint"].split(":")
        folder=OUT/"YAKB.pretty" if lib=="YAKB" else __import__('pathlib').Path(LIB)/(lib+".pretty")
        f=p.FootprintLoad(str(folder),name)
        if f is None: raise RuntimeError(c["footprint"])
        f.SetFPID(p.LIB_ID(lib,name))
        if c["ref"]=="U1":f.SetAttributes(f.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM)
        f.SetReference(c["ref"]);f.SetValue(c["value"])
        # Remove inaccurate upstream Pro Micro models; the mechanical model is explicit.
        if c['kind'] in ['EC','MODULE']: f.Models().clear()
        f.SetPosition(v(c["x"],c["y"]))
        b.Add(f)
        if c["side"]=="B": f.Flip(f.GetPosition(),False)
        if 'rotation' in c: f.SetOrientationDegrees(c['rotation'])
        if c['ref'].startswith('SW'):
            f.Reference().SetPosition(v(c['x'],c['y']-2.5))
            f.Reference().SetTextSize(v(.8,.8))
            f.Reference().SetTextThickness(p.FromMM(.12))
        labels={'C3':(224,88),'R31':(215,91)}
        if c['ref'] in labels:
            f.Reference().SetPosition(v(*labels[c['ref']]))
            f.Reference().SetTextSize(v(.8,.8))
            f.Reference().SetTextThickness(p.FromMM(.12))
        # PTH soldering requires exposed annuli on both sides, independently of
        # the upstream library's copper layer selection.
        for a in f.Pads():
            if a.GetAttribute()==p.PAD_ATTRIB_PTH:
                layers=a.GetLayerSet();layers.AddLayer(p.F_Mask);layers.AddLayer(p.B_Mask);a.SetLayerSet(layers)
        for a in f.Pads():
            name=c["pins"].get(a.GetNumber(),"")
            if name:a.SetNet(nets[name])
        if c["kind"]=="EC":
            for g in f.GraphicalItems():
                if g.GetLayer()==p.F_SilkS:g.SetLayer(p.Dwgs_User)
            f.Reference().SetLayer(p.Dwgs_User)
        f.Value().SetVisible(False)
    # Outer contour, including the Lot60 open side mounting slots. Rounded corners
    # and semicircular slot ends are sampled to <=0.02mm chord error.
    w,h=SPEC["pcb"]["width"],SPEC["pcb"]["height"];r=2;pts=[]
    def arc(cx,cy,rad,start,end,n=16):
        pts.extend((cx+rad*math.cos(math.radians(start+(end-start)*i/n)),cy+rad*math.sin(math.radians(start+(end-start)*i/n))) for i in range(n+1))
    pts.extend([(r,0),(w-r,0)]);arc(w-r,r,r,-90,0)
    a=SPEC["mounts"][-1];rr=a["height"]/2;cx=a["x"]-a["width"]/2+rr
    pts.extend([(w,a["y"]-rr),(cx,a["y"]-rr)]);arc(cx,a["y"],rr,-90,-270);pts.extend([(w,a["y"]+rr),(w,h-r)])
    arc(w-r,h-r,r,0,90);pts.append((r,h));arc(r,h-r,r,90,180)
    a=SPEC["mounts"][0];rr=a["height"]/2;cx=a["x"]+a["width"]/2-rr
    pts.extend([(0,a["y"]+rr),(cx,a["y"]+rr)]);arc(cx,a["y"],rr,90,-90);pts.extend([(0,a["y"]-rr),(0,r)]);arc(r,r,r,180,270)
    for start,end in zip(pts,pts[1:]+pts[:1]):
        if math.dist(start,end)<1e-6:continue
        s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*start));s.SetEnd(v(*end));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)
    for m in SPEC["mounts"][1:-1]:
        f=p.FOOTPRINT(b);f.SetReference("H_"+m["name"]);f.SetAttributes(p.FP_BOARD_ONLY | p.FP_EXCLUDE_FROM_POS_FILES | p.FP_EXCLUDE_FROM_BOM);f.SetPosition(v(m["x"],m["y"]))
        f.Reference().SetVisible(False);f.Value().SetVisible(False)
        if m["name"]=="lower_left":
            for (x1,y1),(x2,y2) in zip([(-3.8,-7.55),(3.8,-7.55),(3.8,7.55),(-3.8,7.55)],[ (3.8,-7.55),(3.8,7.55),(-3.8,7.55),(-3.8,-7.55)]):
                s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(m["x"]+x1,m["y"]+y1));s.SetEnd(v(m["x"]+x2,m["y"]+y2));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)
            continue
        a=p.PAD(f);a.SetAttribute(p.PAD_ATTRIB_NPTH);a.SetShape(p.PAD_SHAPE_OVAL);a.SetDrillShape(p.PAD_DRILL_SHAPE_OBLONG);a.SetSize(v(m["width"],m["height"]));a.SetDrillSize(v(m["width"],m["height"]));a.SetPosition(f.GetPosition());a.SetLayerSet(hole_layers());f.Add(a);b.Add(f)
    ko=SPEC["module"]["antenna_keepout"]
    z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True)
    poly=z.Outline();poly.NewOutline()
    for x,y in [(ko[0],ko[1]),(ko[2],ko[1]),(ko[2],ko[3]),(ko[0],ko[3])]:poly.Append(int(x*1e6),int(y*1e6))
    b.Add(z)
    # Keep inner signal routing and pours out of the active sensor disk.
    inner=p.LSET();inner.AddLayer(p.In1_Cu);inner.AddLayer(p.In2_Cu)
    from common import keys
    for k in keys():
        z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(inner);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(False);z.SetDoNotAllowZoneFills(True)
        poly=z.Outline();poly.NewOutline()
        for n in range(64):poly.Append(p.FromMM(k['x']+6*math.cos(n*math.pi/32)),p.FromMM(k['y']+6*math.sin(n*math.pi/32)))
        b.Add(z)
    text=p.PCB_TEXT(b);text.SetText("YAKB A0 - UNROUTED DESIGN / NOT FOR FAB");text.SetPosition(v(145,69));text.SetTextSize(v(1.1,1.1));text.SetTextThickness(p.FromMM(.15));text.SetLayer(p.B_SilkS);text.SetMirrored(True);b.Add(text)
    # Explicitly preserve schematic NC net names for native parity checks.
    import xml.etree.ElementTree as ET
    for n in ET.parse(ROOT/'reports/schematic.net.xml').findall('./nets/net'):
        if not n.attrib['name'].startswith('unconnected-'):continue
        a=p.NETINFO_ITEM(b,n.attrib['name'].replace('/','{slash}'));b.Add(a)
        for node in n.findall('node'):
            for f in b.GetFootprints():
                if f.GetReference()==node.attrib['ref']:
                    for pad in f.Pads():
                        if pad.GetNumber()==node.attrib['pin']:pad.SetNet(a)
    p.SaveBoard(str(OUT/"YAKB.kicad_pcb"),b)
    (OUT/"fp-lib-table").write_text('(fp_lib_table (version 7) (lib (name "YAKB")(type "KiCad")(uri "${KIPRJMOD}/YAKB.pretty")(options "")(descr "YAKB local footprints")))\n')
    with (OUT/"BOM.csv").open('w') as f:
        out=csv.writer(f,lineterminator='\n');out.writerow(['Reference','Value','Footprint','Side','X_mm','Y_mm','Status'])
        for c in cs:out.writerow([c['ref'],c['value'],c['footprint'],c['side'],c['x'],c['y'],'EC electrode' if c['kind']=='EC' else 'selection; verify procurement'])
    (ROOT/"design/circuit.json").write_text(json.dumps(cs,indent=2)+"\n")
    print(f"Generated {len(cs)} components, {len(nets)} nets, zero tracks (intentional design stage)")

if __name__=="__main__":main()
