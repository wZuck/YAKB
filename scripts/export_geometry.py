"""Export populated KiCad geometry for CAD collision tests and Cycles renders."""
import argparse, hashlib, json, subprocess
from pathlib import Path
import cadquery as cq
from common import ROOT, normalize_text

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kicad-cli',default='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli');args=p.parse_args()
    cache=ROOT/'.render-cache';cache.mkdir(exist_ok=True);board=ROOT/'hardware/YAKB.kicad_pcb'
    subprocess.run([args.kicad_cli,'pcb','export','glb','--force','--include-pads','--include-tracks','--include-silkscreen','--include-soldermask','--cut-vias-in-body','-o',str(ROOT/'mechanical/YAKB-populated.glb'),str(board)],check=True)
    native=cache/'components-native.step'
    subprocess.run([args.kicad_cli,'pcb','export','step','--force','--no-board-body','-o',str(native),str(board)],check=True)
    # KiCad uses PCB bottom z=0 and negative y. YAKB's top datum is z=0.
    shape=cq.importers.importStep(str(native)).val().mirror('XZ').translate((0,0,-1.6))
    cq.exporters.export(shape,str(ROOT/'mechanical/components.step'))
    normalize_text(ROOT/'mechanical/components.step')
    bb=shape.BoundingBox()
    (ROOT/'reports/component-geometry.json').write_text(json.dumps(dict(pcb_sha256=hashlib.sha256(board.read_bytes()).hexdigest(),components_sha256=hashlib.sha256((ROOT/'mechanical/components.step').read_bytes()).hexdigest(),bounds_mm=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax],limitations=['Native library component models; no NiZ internals, cable flex, solder fillets or socket vendor geometry.']),indent=2)+'\n')

if __name__=='__main__':main()
