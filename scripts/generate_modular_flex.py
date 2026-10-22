"""Generate the B1 shaped single-copper-layer FPC, not a straight FFC."""
import json,csv,math
import pcbnew as p,wx
from common import ROOT,normalize_text
from generate_modular_pcbs import board,outline,net,v
from finish_modular_pcbs import schematic
from modular_common import flex_geometry
D=json.loads((ROOT/'design/modular.json').read_text());OUT=ROOT/'hardware/modular'

def bez(t):
 a=D['flex']['controls'];u=1-t
 return (u**3*a[0][0]+3*u*u*t*a[1][0]+3*u*t*t*a[2][0]+t**3*a[3][0],u**3*a[0][1]+3*u*u*t*a[1][1]+3*u*t*t*a[2][1]+t**3*a[3][1])

def main():
 app=wx.App(False);b=board('flex',240,110,.2);points,poly=flex_geometry()
 outline(b,poly)
 ends=[]
 for label,xy in [('A',points[0]),('B',points[-1])]:
  f=p.FOOTPRINT(b);f.SetReference('J_'+label);f.SetValue('FPC_BOTTOM_CONTACT_1mm');f.SetAttributes(p.FP_BOARD_ONLY);b.Add(f);f.Reference().SetVisible(False);f.Value().SetVisible(False);ends.append(f)
 rows=[]
 for i,func in enumerate(D['fpc_pinout']):
  n=net(b,'LINE%02d_%s'%(i+1,func));offset=i-11.5
  for end,f,xy,num in [('A',ends[0],points[0],i+1),('B',ends[1],points[-1],24-i)]:
   pad=p.PAD(f);pad.SetNumber(str(num));pad.SetAttribute(p.PAD_ATTRIB_SMD);pad.SetShape(p.PAD_SHAPE_RECT);pad.SetSize(v(.6,4));pad.SetPosition(v(xy[0]+offset,xy[1]));ls=p.LSET();ls.AddLayer(p.B_Cu);ls.AddLayer(p.B_Mask);pad.SetLayerSet(ls);pad.SetNet(n);f.Add(pad)
  for a,c in zip(points,points[1:]):
   t=p.PCB_TRACK(b);t.SetStart(v(a[0]+offset,a[1]));t.SetEnd(v(c[0]+offset,c[1]));t.SetWidth(p.FromMM(.15));t.SetLayer(p.B_Cu);t.SetNet(n);b.Add(t)
  rows.append([i+1,24-i,func,'bottom contact both ends; connector B rotated 180 degrees'])
 stem='YAKB-shaped-FPC-B1';project=json.loads((ROOT/'hardware/YAKB.kicad_pro').read_text());project['board']['design_settings']['drc_exclusions']=[];(OUT/(stem+'.kicad_pro')).write_text(json.dumps(project,indent=2)+'\n');p.SaveBoard(str(OUT/(stem+'.kicad_pcb')),b);normalize_text(OUT/(stem+'.kicad_pcb'))
 with (OUT/'FPC-pinout.csv').open('w') as f:
  wr=csv.writer(f,lineterminator='\n');wr.writerow(['Carrier_JF1_pin','Interposer_JF1_pin','System_net','Contact_rule']);wr.writerows(rows)
 mapping,libs=schematic(b,stem);lib=OUT/'YAKB_B1.kicad_sym';s=lib.read_text().rstrip();lib.write_text(s[:-1]+''.join(libs)+')\n')
 print('Generated shaped FPC: 24 separate conductors, A:n to B:25-n. No copper pours, no plated holes.')

if __name__=='__main__':main()
