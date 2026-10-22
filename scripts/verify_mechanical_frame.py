"""Verify delivered CAD handedness using asymmetric HHKB solids."""
import cadquery as cq
from common import ROOT


def main():
    bezel=cq.importers.importStep(str(ROOT/'mechanical/case_bezel.step')).val()
    # CAD front is -Y. These probes distinguish a true top view from a mirrored export.
    probes=[((10,-85,9),True),((275,-85,9),True),((40,-85,9),False),((245,-85,9),True),((20,85,9),False)]
    for point,expected in probes:assert bezel.isInside(point)==expected,(point,expected)
    for name in ['pcb_envelope','components','keycap_envelopes','module_envelope']:
        b=cq.importers.importStep(str(ROOT/'mechanical'/(name+'.step'))).val().BoundingBox()
        assert b.ymin<0 and b.ymax<1,name
    print('PASS: delivered CAD is X right / Y rear / Z up; HHKB left 1.5u, right 2.5u; no render reflection.')


if __name__=='__main__':main()
