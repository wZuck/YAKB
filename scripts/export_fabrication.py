"""Export manufacturing files and independent native checks from the saved PCB."""
import argparse
import subprocess
import zipfile
from common import ROOT, normalize_text


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kicad-cli',default='kicad-cli')
    cli=p.parse_args().kicad_cli
    def run(*args):
        subprocess.run([cli,*args],cwd=ROOT,check=True)
    board='hardware/YAKB.kicad_pcb'; schematic='hardware/YAKB.kicad_sch'
    run('sch','export','netlist','--format','kicadxml','-o','reports/schematic.net.xml',schematic)
    run('sch','erc','--format','json','--exit-code-violations','-o','reports/erc.json',schematic)
    run('pcb','drc','--format','json','--schematic-parity','--exit-code-violations','-o','reports/drc.json',board)
    run('sch','export','pdf','-o','hardware/YAKB-schematic.pdf',schematic)
    run('sch','export','svg','-o','assets/schematic/',schematic)
    normalize_text(ROOT/'assets/schematic/YAKB.svg')
    run('pcb','export','gerbers','-o','fabrication/gerbers/','-l','F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts',board)
    run('pcb','export','drill','--excellon-separate-th','--generate-report','--report-path','reports/drill-report.txt','-o','fabrication/gerbers/',board)
    with zipfile.ZipFile(ROOT/'fabrication/YAKB-A0-gerbers.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((ROOT/'fabrication/gerbers').iterdir()):
            if path.is_file():archive.write(path,path.name)


if __name__=='__main__':main()
