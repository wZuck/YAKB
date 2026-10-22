"""Extract actual KiCad pad positions for the local soldering workbench."""
import json
import pcbnew as p
import wx
from common import ROOT

def main():
    app=wx.App(False);b=p.LoadBoard(str(ROOT/'hardware/YAKB.kicad_pcb'));out=[]
    for f in b.GetFootprints():
        if f.GetReference().startswith('H_'):continue
        pads=[]
        for a in f.Pads():
            pads.append(dict(number=a.GetNumber(),x=p.ToMM(a.GetPosition().x),y=p.ToMM(a.GetPosition().y),
                             width=p.ToMM(a.GetSize().x),height=p.ToMM(a.GetSize().y),angle=a.GetOrientationDegrees(),
                             through=a.GetAttribute() in [p.PAD_ATTRIB_PTH,p.PAD_ATTRIB_NPTH],
                             front=a.IsOnLayer(p.F_Cu),back=a.IsOnLayer(p.B_Cu),net=a.GetNetname()))
        out.append(dict(ref=f.GetReference(),value=f.GetValue(),x=p.ToMM(f.GetPosition().x),y=p.ToMM(f.GetPosition().y),pads=pads))
    (ROOT/'design/pad-map.json').write_text(json.dumps(out,indent=2)+'\n');print('Extracted actual pad map')

if __name__=='__main__':main()
