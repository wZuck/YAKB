"""Restore checked copper geometry to a fresh generated PCB; refuse stale data."""
import json,re
import pcbnew as p,wx
from common import ROOT
from export_routing import geometry_hash
from sexpr import children

def main():
 app=wx.App(False);path=ROOT/'hardware/YAKB.kicad_pcb';b=p.LoadBoard(str(path));r=json.loads((ROOT/'design/routing.json').read_text())
 assert r['geometry_sha256']==geometry_hash(),'PCB geometry changed: reroute, do not replay stale copper'
 assert not b.GetTracks(),'Routing restore expects a fresh generated board'
 layers={b.GetLayerName(l):l for l in [p.F_Cu,p.B_Cu,p.In1_Cu,p.In2_Cu]};nets=b.GetNetsByName()
 def v(pt):return p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]))
 for a in r['tracks']:
  if a.get('via'):
   t=p.PCB_VIA(b);t.SetPosition(v(a['at']));t.SetWidth(p.FromMM(a['width']));t.SetDrill(p.FromMM(a['drill']));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
  else:t=p.PCB_TRACK(b);t.SetStart(v(a['a']));t.SetEnd(v(a['b']));t.SetWidth(p.FromMM(a['width']));t.SetLayer(layers[a['layer']])
  t.SetNetCode(nets[a['net']].GetNetCode());t.SetLocked(a['locked']);b.Add(t)
 for d in b.GetDrawings():
  if isinstance(d,p.PCB_TEXT) and 'UNROUTED' in d.GetText():d.SetText('YAKB A0 - ENGINEERING PROTOTYPE / EC VALIDATION REQUIRED')
 p.SaveBoard(str(path),b)
 # Bind physical footprints to the deterministic schematic instances.
 sch=(ROOT/'hardware/YAKB.kicad_sch').read_text();root=re.search(r'\(uuid\s+([^\s)]+)',sch)[1];refs={}
 for _,_,item in children(sch):
  if item.startswith('(symbol (lib_id'):
   ref=re.search(r'\(property "Reference" "([^\"]+)"',item)[1];u=re.search(r'\(uuid\s+([^\s)]+)',item)[1];refs[ref]=f'/{root}/{u}'
 source=path.read_text()
 for a,e,item in reversed(list(children(source))):
  if not item.startswith('(footprint '):continue
  ref=re.search(r'\(property\s+"Reference"\s+"([^\"]+)"',item)
  if ref and ref[1] in refs:
   item=re.sub(r'\(path\s+"[^\"]*"\)\s*','',item)
   item=item[:-1]+f'\n(path "{refs[ref[1]]}")\n)';source=source[:a]+item+source[e:]
 stack='(stackup\n'
 for name,kind,thick in [('F.SilkS','Top Silk Screen',None),('F.Paste','Top Solder Paste',None),('F.Mask','Top Solder Mask',.01),('F.Cu','copper',.035),('dielectric 1','prepreg',.2),('In1.Cu','copper',.035),('dielectric 2','core',1.04),('In2.Cu','copper',.035),('dielectric 3','prepreg',.2),('B.Cu','copper',.035),('B.Mask','Bottom Solder Mask',.01),('B.Paste','Bottom Solder Paste',None),('B.SilkS','Bottom Silk Screen',None)]:
  stack+=f'(layer "{name}" (type "{kind}")'
  if thick is not None:stack+=f'(thickness {thick})'
  if name.startswith('dielectric'):stack+='(material "FR4")(epsilon_r 4.5)(loss_tangent 0.02)'
  if name.endswith('.Mask'):stack+='(color "Green")'
  stack+=')\n'
 stack+='(copper_finish "Immersion gold")(dielectric_constraints no))\n'
 source=source.replace('\t(setup\n','\t(setup\n'+stack,1)
 path.write_text(source);print('Restored checked routing and linked schematic instances')
if __name__=='__main__':main()
