"""Extract actual KiCad pad positions for the local soldering workbench."""
import json, hashlib
import pcbnew as p
import wx
from common import ROOT

def main():
    app=wx.App(False);b=p.LoadBoard(str(ROOT/'hardware/YAKB.kicad_pcb'));out=[]
    def polygons(a,layer):
        shape=p.SHAPE_POLY_SET();a.TransformShapeToPolygon(shape,layer,0,p.FromMM(.004),p.ERROR_OUTSIDE)
        return [[[p.ToMM(shape.COutline(i).CPoint(j).x),p.ToMM(shape.COutline(i).CPoint(j).y)]
                 for j in range(shape.COutline(i).PointCount())] for i in range(shape.OutlineCount())]
    for f in b.GetFootprints():
        if f.GetReference().startswith('H_'):continue
        pads=[]
        for a in f.Pads():
            pads.append(dict(number=a.GetNumber(),x=p.ToMM(a.GetPosition().x),y=p.ToMM(a.GetPosition().y),
                             width=p.ToMM(a.GetSize().x),height=p.ToMM(a.GetSize().y),angle=a.GetOrientationDegrees(),
                             through=a.GetAttribute() in [p.PAD_ATTRIB_PTH,p.PAD_ATTRIB_NPTH],
                             front=a.IsOnLayer(p.F_Cu),back=a.IsOnLayer(p.B_Cu),net=a.GetNetname(),
                             front_mask=a.IsOnLayer(p.F_Mask),back_mask=a.IsOnLayer(p.B_Mask),
                             drill=[p.ToMM(a.GetDrillSize().x),p.ToMM(a.GetDrillSize().y)],
                             front_polygons=polygons(a,p.F_Cu) if a.IsOnLayer(p.F_Cu) else [],
                             back_polygons=polygons(a,p.B_Cu) if a.IsOnLayer(p.B_Cu) else []))
        out.append(dict(ref=f.GetReference(),value=f.GetValue(),x=p.ToMM(f.GetPosition().x),y=p.ToMM(f.GetPosition().y),
                        side=f.GetLayerName(),angle=f.GetOrientationDegrees(),pads=pads,
                        models=[dict(path=str(m.m_Filename),offset=[m.m_Offset.x,m.m_Offset.y,m.m_Offset.z],
                                     rotate=[m.m_Rotation.x,m.m_Rotation.y,m.m_Rotation.z]) for m in f.Models()]))
    (ROOT/'design/pad-map.json').write_text(json.dumps(out,indent=2)+'\n');print('Extracted actual pad map')
    tracks=[]
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):tracks.append(dict(via=True,at=[p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)],width=p.ToMM(t.GetWidth(p.F_Cu)),drill=p.ToMM(t.GetDrillValue()),net=t.GetNetname()))
        else:tracks.append(dict(layer=t.GetLayerName(),a=[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],b=[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)],width=p.ToMM(t.GetWidth()),net=t.GetNetname()))
    edges=[]
    for d in b.GetDrawings():
        if isinstance(d,p.PCB_SHAPE) and d.GetLayer()==p.Edge_Cuts:
            edges.append([[p.ToMM(d.GetStart().x),p.ToMM(d.GetStart().y)],[p.ToMM(d.GetEnd().x),p.ToMM(d.GetEnd().y)]])
    holes=[dict(at=[p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)],
                size=[p.ToMM(a.GetDrillSize().x),p.ToMM(a.GetDrillSize().y)],angle=a.GetOrientationDegrees())
           for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()==p.PAD_ATTRIB_NPTH]
    (ROOT/'design/pcb-scene.json').write_text(json.dumps(dict(pcb_sha256=hashlib.sha256((ROOT/'hardware/YAKB.kicad_pcb').read_bytes()).hexdigest(),tracks=tracks,edges=edges,holes=holes),indent=2)+'\n')

if __name__=='__main__':main()
