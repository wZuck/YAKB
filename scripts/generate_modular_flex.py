"""Generate the installed B1 FPC and a short mating coupon from one interface contract."""
import json,csv,re
import pcbnew as p,wx
from common import ROOT,normalize_text
from generate_modular_pcbs import board,outline,net,v
from finish_modular_pcbs import schematic
from modular_common import flex_geometry,I,D,clip_y
from sexpr import children
OUT=ROOT/'hardware/modular'
def main():
 app=wx.App(False);boards=[]
 for coupon,stem in [(False,'YAKB-shaped-FPC-B1'),(True,'YAKB-FPC-coupon-B1')]:
  b=board('flex',240,110,.2);b.GetTitleBlock().SetRevision('B1.1');b.GetTitleBlock().SetTitle(stem);b.GetTitleBlock().SetDate('2026-10-23');boards.append(b);points,poly=flex_geometry(coupon);outline(b,poly);ends=[];rows=[]
  for label,xy in [('A',points[0]),('B',points[-1])]:
   f=p.FOOTPRINT(b);f.SetReference('J_'+label);f.SetValue('MOLEX_200528_1mm_BOTTOM');f.SetAttributes(p.FP_BOARD_ONLY);f.SetAllowSolderMaskBridges(True);b.Add(f);f.Reference().SetVisible(False);f.Value().SetVisible(False);ends.append(f)
   # One continuous coverlay opening, not 24 narrow coverlay slots.
   s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_RECT);s.SetStart(v(xy[0]-12.5,xy[1]-1.75));s.SetEnd(v(xy[0]+12.5,xy[1]+1.75));s.SetLayer(p.B_Mask);s.SetWidth(0);s.SetFilled(True);f.Add(s)
  for index,xy in enumerate([points[0],points[-1]]):
   tip=xy[1]+(-1 if index==0 else 1)*1.75;start=tip if index==0 else tip-5;polygon=p.SHAPE_POLY_SET();polygon.NewOutline()
   for x,y in clip_y(poly,start,start+5):polygon.Append(p.FromMM(x),p.FromMM(y))
   shape=p.PCB_SHAPE();shape.SetShape(p.SHAPE_T_POLY);shape.SetPolyShape(polygon);shape.SetLayer(p.F_Adhes);shape.SetFilled(True);shape.SetWidth(0);b.Add(shape)
  for i,func in enumerate(D['fpc_pinout']):
   n=net(b,'LINE%02d_%s'%(i+1,func));offset=i-11.5
   for f,xy,num in [(ends[0],points[0],i+1),(ends[1],points[-1],24-i)]:
    pad=p.PAD(f);pad.SetNumber(str(num));pad.SetAttribute(p.PAD_ATTRIB_SMD);pad.SetShape(p.PAD_SHAPE_RECT);pad.SetSize(v(I['finger_width_mm'],I['finger_length_mm']));pad.SetPosition(v(xy[0]+offset,xy[1]));ls=p.LSET();ls.AddLayer(p.B_Cu);pad.SetLayerSet(ls);pad.SetNet(n);f.Add(pad)
   for a,c in zip(points,points[1:]):
    t=p.PCB_TRACK(b);t.SetStart(v(a[0]+offset,a[1]));t.SetEnd(v(c[0]+offset,c[1]));t.SetWidth(p.FromMM(.15));t.SetLayer(p.B_Cu);t.SetNet(n);b.Add(t)
   rows.append([i+1,24-i,func,'bottom contact both ends; connector B rotated 180 degrees'])
  p.SaveBoard(str(OUT/(stem+'.kicad_pcb')),b);normalize_text(OUT/(stem+'.kicad_pcb'))
  # Exposed edge fingers intentionally reach the cut edge. All other copper keeps the global clearance.
  (OUT/(stem+'.kicad_dru')).write_text('(version 1)\n(rule "Exposed insertion-edge fingers" (condition "A.Type == \'Pad\'") (constraint edge_clearance (min -0.05mm)))\n')
  mapping,libs=schematic(b,stem);lib=OUT/'YAKB_B1.kicad_sym';source=lib.read_text()
  for a,e,item in reversed(list(children(source))):
   if item.startswith('(symbol "'+stem+'_'):source=source[:a]+source[e:]
  lib.write_text(source.rstrip()[:-1]+''.join(libs)+')\n')
  if not coupon:
   with (OUT/'FPC-pinout.csv').open('w') as f:
    wr=csv.writer(f,lineterminator='\n');wr.writerow(['Carrier_JF1_pin','Interposer_JF1_pin','System_net','Contact_rule']);wr.writerows(rows)
 print('Generated document-derived 25mm tabs / ears / 0.7x3.5mm fingers, continuous coverlay windows and mating coupon.')
if __name__=='__main__':main()
