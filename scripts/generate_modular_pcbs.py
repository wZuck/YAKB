"""Generate B1 carrier/interposer and a shaped flex; run with KiCad Python."""
import sys,json,csv,math
from pathlib import Path
import pcbnew as p
import wx
from common import ROOT
from circuit import components
from generate_pcb import v,hole_layers
D=json.loads((ROOT/'design/modular.json').read_text());OUT=ROOT/'hardware/modular'
LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')

def board(name,w,h,thick=1):
 b=p.BOARD();b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(p.FromMM(thick))
 return b

def outline(b,points):
 for a,c in zip(points,points[1:]+points[:1]):
  s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*c));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)

def net(b,name):
 for n in b.GetNetsByNetcode().values():
  if n.GetNetname()==name:return n
 n=p.NETINFO_ITEM(b,name);b.Add(n);return n

def footprint(b,lib,name,ref,value,x,y,pins,flip=False):
 folder=ROOT/'hardware/YAKB.pretty' if lib=='YAKB' else LIB/(lib+'.pretty')
 f=p.FootprintLoad(str(folder),name);assert f,(lib,name);f.SetFPID(p.LIB_ID(lib,name));f.SetReference(ref);f.SetValue(value);b.Add(f);f.SetPosition(v(x,y))
 if flip:f.Flip(f.GetPosition(),False)
 for a in f.Pads():
  if a.GetNumber() in pins:a.SetNet(net(b,pins[a.GetNumber()]))
  if a.GetAttribute()==p.PAD_ATTRIB_PTH:a.SetLayerSet(hole_layers())
 f.Reference().SetVisible(False);f.Value().SetVisible(False)
 return f

def ff(b,center,reverse=False):
 f=footprint(b,'Connector_FFC-FPC',D['connector_footprint'],'JF1',D['connector'],*center,{str(i+1):s for i,s in enumerate(list(reversed(D['fpc_pinout'])) if reverse else D['fpc_pinout'])})
 if reverse:f.SetOrientationDegrees(180)
 for a in f.Pads():
  if a.GetNumber()=='MP':a.SetNet(net(b,'GND'))
 return f

def keepout(b,points):
 z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowPads(False);z.Outline().NewOutline()
 for x,y in points:z.Outline().Append(p.FromMM(x),p.FromMM(y))
 b.Add(z)

def save(b,name):
 # Silkscreen-free prototype avoids hiding fine-pitch joints with text.
 p.SaveBoard(str(OUT/(name+'.kicad_pcb')),b)
 (ROOT/'.render-cache').mkdir(exist_ok=True);p.SaveBoard(str(ROOT/'.render-cache'/(name+'-unrouted.kicad_pcb')),b)
 project=json.loads((ROOT/'hardware/YAKB.kicad_pro').read_text())
 project['board']['design_settings']['drc_exclusions']=[]
 (OUT/(name+'.kicad_pro')).write_text(json.dumps(project,indent=2)+'\n')
 with (OUT/(name+'-netlist.csv')).open('w') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['Reference','Value','Pad','Net','X_mm','Y_mm'])
  for fp in b.GetFootprints():
   for a in fp.Pads():w.writerow([fp.GetReference(),fp.GetValue(),a.GetNumber(),a.GetNetname(),p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)])
 # Specctra export is API-supported in KiCad; router output is kept separately.
 p.ExportSpecctraDSN(b,str(OUT/(name+'.dsn')))


def main():
 app=wx.App(False);OUT.mkdir(exist_ok=True)
 u=next(c for c in components() if c['ref']=='U1');pins=u['pins']
 b=board('carrier',82,24);outline(b,[(0,0),(82,0),(82,24),(0,24)])
 # Top-mounted nice!nano; physical pad numbers are invariant, y differs from the underside A0 footprint.
 f=footprint(b,'YAKB','nice_nano','U1','nice!nano_v2',*D['carrier']['module_footprint_center'],{k:('ADC_FLEX' if x=='ADC' else x) for k,x in pins.items() if x})
 f.Models().clear();ff(b,D['carrier']['fpc_center'])
 footprint(b,'Capacitor_SMD','C_0805_2012Metric_Pad1.18x1.45mm_HandSolder','C1','1nF_C0G',38,22,{"1":"ADC_FLEX","2":"GND"})
 footprint(b,'Capacitor_SMD','C_0805_2012Metric_Pad1.18x1.45mm_HandSolder','C2','100nF',52,4,{"1":"VCC","2":"GND"})
 for i,(x,y) in enumerate(D['carrier']['mounts']):
  h=p.FOOTPRINT(b);h.SetReference('H'+str(i+1));h.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM);b.Add(h)
  a=p.PAD(h);a.SetAttribute(p.PAD_ATTRIB_NPTH);a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetSize(v(2.3,2.3));a.SetDrillSize(v(2.3,2.3));a.SetPosition(v(x,y));a.SetLayerSet(hole_layers());h.Add(a);h.Reference().SetVisible(False);h.Value().SetVisible(False)
  keepout(b,[(x-1.65,y-1.65),(x+1.65,y-1.65),(x+1.65,y+1.65),(x-1.65,y+1.65)])
 ko=D['carrier']['antenna_keepout'];z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True);z.Outline().NewOutline()
 for x,y in [(ko[0],ko[1]),(ko[2],ko[1]),(ko[2],ko[3]),(ko[0],ko[3])]:z.Outline().Append(int(x*1e6),int(y*1e6))
 b.Add(z);save(b,'YAKB-controller-B1');carrier_board=b
 b=board('interposer',40,19);outline(b,[(0,0),(40,0),(40,19),(0,19)])
 main=p.LoadBoard(str(ROOT/'hardware/YAKB.kicad_pcb'));original=next(f for f in main.GetFootprints() if f.GetReference()=='U1')
 f=p.FOOTPRINT(b);f.SetReference('JMAIN');f.SetAttributes(p.FP_THROUGH_HOLE);f.SetValue('A0_U1_socket_NO_MCU');b.Add(f)
 for old in original.Pads():
  a=p.PAD(f);a.SetNumber(old.GetNumber());a.SetAttribute(p.PAD_ATTRIB_PTH);a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetSize(v(1.8,1.8));a.SetDrillSize(v(1,1));a.SetLayerSet(hole_layers());a.SetPosition(v(p.ToMM(old.GetPosition().x)-240,p.ToMM(old.GetPosition().y)-75.5))
  n=pins.get(a.GetNumber(),'')
  if n:a.SetNet(net(b,n))
  f.Add(a)
 f.Reference().SetVisible(False);f.Value().SetVisible(False)
 f.SetFPID(p.LIB_ID('YAKB_MOD','A0_U1_socket_adapter'))
 ff(b,D['interposer']['fpc_center'],reverse=True)
 footprint(b,'Resistor_SMD','R_0805_2012Metric_Pad1.20x1.40mm_HandSolder','R1','47',37.5,13,{"1":"ADC","2":"ADC_FLEX"})
 save(b,'YAKB-interposer-B1')
 print('Generated carrier and interposer native PCBs/netlists/DSN; route and run native DRC before manufacturing.')

if __name__=='__main__':main()
