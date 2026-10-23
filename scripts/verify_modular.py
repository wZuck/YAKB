"""Verify the saved B1 native pad chain, A0 hole alignment and native check reports.

Run with KiCad Python. The 47 ohm resistor is the sole intentional net-name change.
"""
import json,csv,hashlib,math
from pathlib import Path
import pcbnew as p,wx
from common import ROOT
from modular_common import flex_geometry
from collections import Counter
D=json.loads((ROOT/'design/modular.json').read_text());OUT=ROOT/'reports/modular'
def main():
 app=wx.App(False);names=['controller','interposer','shaped-FPC','FPC-coupon'];boards={n:p.LoadBoard(str(ROOT/'hardware/modular'/('YAKB-'+n+'-B1.kicad_pcb'))) for n in names}
 main=p.LoadBoard(str(ROOT/'hardware/YAKB.kicad_pcb'));fps={n:{f.GetReference():f for f in b.GetFootprints()} for n,b in boards.items()}
 def pads(fp):return {a.GetNumber():a for a in fp.Pads() if a.GetNumber()!='MP'}
 old=pads(next(f for f in main.GetFootprints() if f.GetReference()=='U1'));adapter=pads(fps['interposer']['JMAIN']);mcu=pads(fps['controller']['U1']);a=pads(fps['controller']['JF1']);b=pads(fps['interposer']['JF1']);fa=pads(fps['shaped-FPC']['J_A']);fb=pads(fps['shaped-FPC']['J_B']);checks=[]
 for num,pad in old.items():
  ip=adapter[num];x,y,_=D['interposer']['world_origin'];err=math.hypot(p.ToMM(pad.GetPosition().x)-p.ToMM(ip.GetPosition().x)-x,p.ToMM(pad.GetPosition().y)-p.ToMM(ip.GetPosition().y)-y);assert err<.0001,(num,err)
  net=pad.GetNetname()
  if not net or net.startswith('unconnected-('):continue
  assert ip.GetNetname()==net,(num,'A0->interposer')
  end='ADC_FLEX' if net=='ADC' else net;assert mcu[num].GetNetname()==end,(num,'MCU')
  checks.append({'A0_U1_pad':num,'A0_net':net,'carrier_net':end,'hole_alignment_error_mm':round(err,6)})
 for i,net in enumerate(D['fpc_pinout'],1):
  j=25-i;assert a[str(i)].GetNetname()==b[str(j)].GetNetname()==net,(i,j,net)
  assert fa[str(i)].GetNetname()==fb[str(j)].GetNetname()=='LINE%02d_%s'%(i,net)
 interface=json.loads((ROOT/'design/fpc-interface.json').read_text())
 for name in ['shaped-FPC','FPC-coupon']:
  aa=pads(fps[name]['J_A']);bb=pads(fps[name]['J_B']);assert set(fps[name])=={'J_A','J_B'}
  _,poly=flex_geometry(name=='FPC-coupon')
  expected=Counter(tuple(sorted(((round(a[0]*1e6),round(a[1]*1e6)),(round(b[0]*1e6),round(b[1]*1e6))))) for a,b in zip(poly,poly[1:]+poly[:1]))
  actual=Counter(tuple(sorted(((s.GetStart().x,s.GetStart().y),(s.GetEnd().x,s.GetEnd().y)))) for s in boards[name].GetDrawings() if s.GetLayer()==p.Edge_Cuts)
  assert actual==expected,(name,'Native edge outline differs from interface geometry')
  assert all(f.AllowSolderMaskBridges() for f in boards[name].GetFootprints())
  for i,func in enumerate(D['fpc_pinout'],1):
   assert aa[str(i)].GetNetname()==bb[str(25-i)].GetNetname()=='LINE%02d_%s'%(i,func)
   for pad in [aa[str(i)],bb[str(25-i)]]:
    assert abs(p.ToMM(pad.GetSize().x)-.7)<1e-6 and abs(p.ToMM(pad.GetSize().y)-3.5)<1e-6
    assert not pad.GetLayerSet().Contains(p.B_Mask),'Coverlay must be one contiguous opening'
  windows=[s for f in boards[name].GetFootprints() for s in f.GraphicalItems() if s.GetLayer()==p.B_Mask]
  assert len(windows)==2
  assert len([s for s in boards[name].GetDrawings() if s.GetLayer()==p.F_Adhes])==2
  for s in windows:assert abs(abs(p.ToMM(s.GetEnd().x-s.GetStart().x))-25)<1e-6 and abs(abs(p.ToMM(s.GetEnd().y-s.GetStart().y))-3.5)<1e-6
 depths=[]
 for ref,end,origin,sign in [('A',0,D['carrier']['world_origin'],1),('B',1,D['interposer']['world_origin'],-1)]:
  f=fps['controller' if ref=='A' else 'interposer']['JF1'];mouth=origin[1]+p.ToMM(f.GetPosition().y)+sign*4.19;tip=D['flex']['contacts'][end][1]-sign*1.75;depth=sign*(mouth-tip);assert abs(depth-4)<1e-6;depths.append(depth)
 for i in range(1,25):
  assert abs(p.ToMM(fa[str(i)].GetPosition().x)-(D['carrier']['world_origin'][0]+p.ToMM(a[str(i)].GetPosition().x)))<1e-6
  assert abs(p.ToMM(fb[str(25-i)].GetPosition().x)-(D['interposer']['world_origin'][0]+p.ToMM(b[str(25-i)].GetPosition().x)))<1e-6
 r=pads(fps['interposer']['R1']);assert [r[str(i)].GetNetname() for i in [1,2]]==['ADC','ADC_FLEX']
 for name in names:
  for kind in ['erc','drc']:
   d=json.loads((OUT/('YAKB-'+name+'-B1-'+kind+'.json')).read_text());assert not d.get('violations') and not d.get('schematic_parity') and not d.get('unconnected_items'),(name,kind)
 # Persist native geometry for 2D drawings; never recreate routed lines from a conceptual diagram.
 geometry={}
 for name,board in boards.items():
  geometry[name]={'pads':[dict(ref=f.GetReference(),number=a.GetNumber(),net=a.GetNetname(),x=p.ToMM(a.GetPosition().x),y=p.ToMM(a.GetPosition().y),w=p.ToMM(a.GetSize().x),h=p.ToMM(a.GetSize().y),drill=p.ToMM(a.GetDrillSize().x),circle=a.GetShape()==p.PAD_SHAPE_CIRCLE,radius=p.ToMM(a.GetRoundRectCornerRadius()) if a.GetShape()==p.PAD_SHAPE_ROUNDRECT else 0,angle=a.GetOrientationDegrees()) for f in board.GetFootprints() for a in f.Pads()], 'tracks':[dict(x1=p.ToMM(t.GetStart().x),y1=p.ToMM(t.GetStart().y),x2=p.ToMM(t.GetEnd().x),y2=p.ToMM(t.GetEnd().y),width=p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()),layer=t.GetLayerName(),net=t.GetNetname(),drill=p.ToMM(t.GetDrillValue()) if isinstance(t,p.PCB_VIA) else 0) for t in board.GetTracks()]}
 (ROOT/'.render-cache/modular-native-geometry.json').write_text(json.dumps(geometry))
 sources={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['hardware/YAKB.kicad_pcb','design/modular.json']+[str(Path('hardware/modular')/('YAKB-'+n+'-B1.kicad_pcb')) for n in names]}
 report={'native_pad_paths':checks,'FPC_contacts_verified':24,'coupon_contacts_verified':24,'derived_insertion_depths_mm':depths,'mapping':'A:n -> B:25-n','native_DRC_ERC_parity_unconnected':0,'sources':sources,'limits':['Electrical rule checks do not model RF, charging transients or ADC noise.','All modular schematics use passive physical-pin symbols; they check connectivity, not internal nice!nano circuitry.']}
 extra=['scripts/finish_modular_pcbs.py','design/fpc-interface.json','scripts/generate_modular_flex.py','hardware/modular/YAKB-shaped-FPC-B1.kicad_dru','hardware/modular/YAKB-FPC-coupon-B1.kicad_dru','scripts/verify_modular.py','scripts/export_modular.py','scripts/modular_common.py','hardware/modular/YAKB_B1.kicad_sym','hardware/modular/fp-lib-table','hardware/modular/sym-lib-table','hardware/modular/YAKB_MOD.pretty/A0_U1_socket_adapter.kicad_mod']+['hardware/modular/YAKB-'+n+'-B1'+ext for n in names for ext in ['.kicad_sch','.kicad_pro']]
 report['sources'].update({f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in extra})
 artifacts=list(OUT.glob('*-erc.json'))+list(OUT.glob('*-drc.json'))+list(OUT.glob('*-net.xml'))+list((ROOT/'hardware/modular').glob('*.pdf'))+list((ROOT/'mechanical/modular').glob('*.glb'))+list((ROOT/'mechanical/modular').glob('*-native.step'))+[f for f in (ROOT/'fabrication/modular').rglob('*') if f.is_file()]
 report['outputs']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in artifacts}
 (OUT/'connectivity.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Verified 24 cable contacts, %d used module pads, exact A0 header coordinates and all native reports.'%len(checks))
if __name__=='__main__':main()
