"""Import routes, export authoritative native pad maps and standalone schematics."""
import json,csv,re,uuid
from pathlib import Path
import pcbnew as p,wx
from common import ROOT,normalize_text
from generate_pcb import v
from generate_modular_pcbs import net
from sexpr import children
OUT=ROOT/'hardware/modular'

def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/wZuck/YAKB/B1/'+s))
def q(s):return json.dumps(str(s))
def fx():return '(effects (font (size 1 1)))'
def schematic(b,stem):
 libs=[];items=[];mapping={};symbol_lib=[]
 for idx,f in enumerate(f for f in b.GetFootprints() if not f.GetReference().startswith('H')):
  ref=f.GetReference();pins={a.GetNumber():('' if a.GetNetname().startswith('unconnected-(') else a.GetNetname()) for a in f.Pads()};nums=sorted(pins,key=lambda x:(not x.isdigit(),int(x) if x.isdigit() else x));n=(len(nums)+1)//2;h=(n+1)*2.54;w=15.24;x=round((35+idx*55)/1.27)*1.27;y=round(65/1.27)*1.27
  name=stem+'_'+ref;id='YAKB_B1:'+name;graphics=f'(rectangle (start {-w} {-h/2}) (end {w} {h/2}) (stroke (width .254) (type default)) (fill (type background)))';ps=[];coords={}
  for i,num in enumerate(nums):
   left=i<n;j=i if left else i-n;px=-w-2.54 if left else w+2.54;py=(n-1)*2.54/2-j*2.54;angle=0 if left else 180;coords[num]=(px,py,angle)
   ps.append(f'(pin passive line (at {px} {py} {angle}) (length 2.54) (name {q(pins[num] or "NC")} {fx()}) (number {q(num)} {fx()}))')
  lib=f'(symbol {q(id)} (pin_names (offset .5)) (in_bom yes) (on_board yes) (property "Reference" {q(ref)} (at 0 {h/2+2.54} 0) {fx()}) (property "Value" {q(f.GetValue())} (at 0 {-h/2-2.54} 0) {fx()}) (symbol {q(name+"_0_1")} {graphics}) (symbol {q(name+"_1_1")} {"".join(ps)}))';libs.append(lib);symbol_lib.append(lib.replace(q(id),q(name),1))
  sid=uid(stem+ref);mapping[ref]=sid
  props=f'(property "Reference" {q(ref)} (at {x} {y-h/2-2.54} 0) {fx()}) (property "Value" {q(f.GetValue())} (at {x} {y+h/2+2.54} 0) {fx()}) (property "Footprint" {q(f.GetFPID().GetUniStringLibId())} (at {x} {y} 0) (effects (font (size 1 1)) hide))'
  items.append(f'(symbol (lib_id {q(id)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {sid}) {props} (instances (project {q(stem)} (path "/{uid(stem)}" (reference {q(ref)}) (unit 1)))))')
  for num,(px,py,angle) in coords.items():
   ax=x+px;ay=y-py;net=pins[num]
   if not net:items.append(f'(no_connect (at {ax} {ay}) (uuid {uid(stem+ref+num+"nc")}))');continue
   end=ax+(-5.08 if px<0 else 5.08);items.append(f'(wire (pts (xy {ax} {ay}) (xy {end} {ay})) (stroke (width 0) (type default)) (uuid {uid(stem+ref+num+"w")}))');items.append(f'(global_label {q(net)} (shape bidirectional) (at {end} {ay} {0 if px<0 else 180}) (effects (font (size 1 1)) (justify {"right" if px<0 else "left"} bottom)) (uuid {uid(stem+ref+num+"l")}))')
 sch=f'(kicad_sch (version 20250114) (generator "yakb") (uuid {uid(stem)}) (paper "A4") (title_block (title {q(stem+" ENGINEERING PROTOTYPE")}) (rev "B1")) (lib_symbols {"".join(libs)}) {"".join(items)})\n';(OUT/(stem+'.kicad_sch')).write_text(sch)
 return mapping,symbol_lib

def import_routes(b,path):
 assert len(b.GetTracks())==0, "Load the unrouted source; never import duplicate tracks"
 tokens=re.findall(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()]+',path.read_text());it=iter(tokens)
 def parse():
  result=[]
  for t in it:
   if t==')':return result
   result.append(parse() if t=='(' else json.loads(t) if t.startswith('"') else t)
  return result
 tree=parse()
 def find(node,key):
  if isinstance(node,list):
   if node and node[0]==key:yield node
   for a in node:yield from find(a,key)
 for node in find(tree,'net'):
  if node[1] not in b.GetNetsByName():continue
  n=b.GetNetsByName()[node[1]]
  for path in find(node,'path'):
   layer=p.F_Cu if path[1]=='F.Cu' else p.B_Cu;width=float(path[2])/10000
   points=[(float(path[i])/10000,-float(path[i+1])/10000) for i in range(3,len(path),2)]
   for a,c in zip(points,points[1:]):
    t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*c));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(n);b.Add(t)
  for via in find(node,'via'):
   t=p.PCB_VIA(b);t.SetPosition(v(float(via[2])/10000,-float(via[3])/10000));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(n);b.Add(t)
 assert len(b.GetTracks())>0

def main():
 app=wx.App(False);all_lib=[]
 for stem in ['YAKB-controller-B1','YAKB-interposer-B1']:
  path=OUT/(stem+'.kicad_pcb');b=p.LoadBoard(str(ROOT/'.render-cache'/(stem+'-unrouted.kicad_pcb')));import_routes(b,OUT/(stem+'.ses'))
  for fp in b.GetFootprints():
   if fp.GetReference()=='JMAIN':fp.SetAttributes(p.FP_THROUGH_HOLE)
  mapping,libs=schematic(b,stem);all_lib+=libs
  for fp in b.GetFootprints():
   for pad in fp.Pads():
    if pad.GetNumber() and not pad.GetNetname():pad.SetNet(net(b,'unconnected-(%s-NC-Pad%s)'%(fp.GetReference(),pad.GetNumber())))
  p.SaveBoard(str(path),b)
  # Preserve schematic NC net names for parity.
  source=path.read_text()
  for a,e,item in reversed(list(children(source))):
   if not item.startswith('(footprint '):continue
   ref=re.search(r'\(property\s+"Reference"\s+"([^"]+)"',item)
   if ref and ref[1] in mapping:item=item[:-1]+'\n(path "/'+uid(stem)+'/'+mapping[ref[1]]+'")\n)';source=source[:a]+item+source[e:]
  path.write_text(source);custom=OUT/'YAKB_MOD.pretty';custom.mkdir(exist_ok=True)
  for _,_,item in children(source):
   if item.startswith('(footprint "YAKB_MOD:'):
    item=re.sub(r'^\(footprint "YAKB_MOD:[^"]+"','(footprint "A0_U1_socket_adapter"',item)
    (custom/'A0_U1_socket_adapter.kicad_mod').write_text(item+'\n');normalize_text(custom/'A0_U1_socket_adapter.kicad_mod')
  normalize_text(path)
 (OUT/'YAKB_B1.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "yakb") '+''.join(all_lib)+')\n')
 (OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "YAKB_B1") (type "KiCad") (uri "${KIPRJMOD}/YAKB_B1.kicad_sym") (options "") (descr "B1 exact physical pins")))\n')
 (OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "YAKB") (type "KiCad") (uri "${KIPRJMOD}/../YAKB.pretty") (options "") (descr "A0 module footprint")) (lib (name "YAKB_MOD") (type "KiCad") (uri "${KIPRJMOD}/YAKB_MOD.pretty") (options "") (descr "B1 interposer")))\n')
 print('Imported both routed boards and generated standalone native schematics.')

if __name__=='__main__':main()
