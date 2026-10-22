"""Native B1 ERC/DRC, fabrication, schematic and populated geometry exports."""
import json,hashlib,subprocess,zipfile
from pathlib import Path
from common import ROOT,normalize_text
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
STEMS=['YAKB-controller-B1','YAKB-interposer-B1','YAKB-shaped-FPC-B1']
def run(*args):subprocess.run([CLI,*map(str,args)],cwd=ROOT,check=True)
def package(stem,target):
 if 'FPC' in stem:
  # KiCad requires >=2 logical copper layers. Its default job stack is invalid for this single-sided flex.
  for f in target.glob('*.gbrjob'):f.unlink()
  for f in target.glob('*B_Cu.gbl'):f.write_text(f.read_text().replace('TF.FileFunction,Copper,L2,Bot','TF.FileFunction,Copper,L1,Bot'))
  spec=json.loads((ROOT/'design/modular.json').read_text())['flex']
  (target/'FLEX-STACKUP.json').write_text(json.dumps(dict(status='ENGINEERING PROTOTYPE - mating drawing/sample qualification required',physical_copper_layers=1,copper_file='B_Cu.gbl',copper_um=spec['copper_um'],nominal_finished_flex_thickness_mm=spec['thickness_mm'],substrate='polyimide; supplier-engineered dielectric/adhesive/coverlay stack',coverlay='B.Mask defines exposed contact windows; use flexible coverlay',stiffened_terminal_thickness_mm=spec['ends_stiffened_thickness_mm'],terminal_status='UNQUALIFIED: thickness, face, length, insertion depth and finish must be confirmed with Molex 200528-0240 mating drawing/samples',static_installation=True),indent=2)+'\n')
  (target/'FABRICATION-NOTES.txt').write_text('YAKB B1 CUSTOM SINGLE-SIDED FLEX - ENGINEERING PROTOTYPE\nDo not use the default rigid FR4 / two-layer stack. B.Cu is the only physical copper layer.\nRead FLEX-STACKUP.json and docs/modular/README.md before quoting.\nSTOP full-flex manufacture until the connector mating coupon is qualified.\n0.30 mm stiffened ends, exposed finger dimensions and contact elevation remain unqualified.\n')
 with zipfile.ZipFile(target.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(target.iterdir()):z.write(f,f.name)

def main():
 out=ROOT/'reports/modular';out.mkdir(exist_ok=True);cad=ROOT/'mechanical/modular';cad.mkdir(exist_ok=True)
 for stem in STEMS:
  pcb=ROOT/'hardware/modular'/(stem+'.kicad_pcb');sch=pcb.with_suffix('.kicad_sch')
  project=json.loads((ROOT/'hardware/YAKB.kicad_pro').read_text());project['board']['design_settings']['drc_exclusions']=[];project['meta']['filename']=stem+'.kicad_pro'
  if 'FPC' in stem:
   project['board']['design_settings']['rules']['min_clearance']=.10;project['board']['design_settings']['rules']['min_copper_edge_clearance']=.20;project['net_settings']['classes'][0]['clearance']=.10
  pcb.with_suffix('.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
  run('sch','erc','--format','json','--exit-code-violations','-o',out/(stem+'-erc.json'),sch)
  run('pcb','drc','--format','json','--schematic-parity','--exit-code-violations','-o',out/(stem+'-drc.json'),pcb)
  run('sch','export','netlist','--format','kicadxml','-o',out/(stem+'-net.xml'),sch)
  run('sch','export','pdf','-o',sch.with_suffix('.pdf'),sch)
  run('pcb','export','glb','--force','--include-pads','--include-tracks','--include-silkscreen','--include-soldermask','--cut-vias-in-body','-o',cad/(stem+'.glb'),pcb)
  run('pcb','export','step','--force','-o',cad/(stem+'-native.step'),pcb)
  target=ROOT/'fabrication/modular'/stem;target.mkdir(parents=True,exist_ok=True)
  layers='B.Cu,B.Mask,Edge.Cuts' if 'FPC' in stem else 'F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts'
  run('pcb','export','gerbers','-o',str(target)+'/', '-l',layers,pcb)
  if 'FPC' not in stem:run('pcb','export','drill','--excellon-separate-th','-o',str(target)+'/',pcb)
  package(stem,target)
  normalize_text(cad/(stem+'-native.step'))
 print('B1 native outputs exported; Gerbers are engineering prototypes, not a production approval.')
if __name__=='__main__':main()
