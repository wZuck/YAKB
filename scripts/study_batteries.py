"""Evaluate optional factory-built 1S multi-pouch packs against delivered CAD."""
import json,hashlib
import cadquery as cq
from common import ROOT,SPEC,normalize_text
from generate_mechanical import box,plane_halfspace,floor_z,ANGLE,FLOOR_INTERCEPT
import math


def main():
    folder=ROOT/'mechanical';base=cq.importers.importStep(str(folder/'case_base.step')).mirror('XZ')
    parts={n:cq.importers.importStep(str(folder/(n+'.step'))).mirror('XZ') for n in ['pcb_envelope','components','module_envelope','usb_plug_envelope','case_screw_envelopes']}
    w,h,t=SPEC['battery']['max_envelope'];bays=[];pouches=[];variant=base
    for x in [62,144,226]:
        y,z=23,-7.8
        cell=box(x-w/2,y-h/2,z-t/2,w,h,t).rotate((x,y,z),(x+1,y,z),ANGLE);pouches.append(cell)
        overlaps={n:round(cell.intersect(shape).val().Volume(),6) if cell.intersect(shape).vals() else 0 for n,shape in {'base':base,**parts}.items()}
        assert all(v<.001 for v in overlaps.values())
        bays.append(dict(center_mm=[x,y,z],max_pouch_envelope_mm=[w,h,t],intersections_mm3=overlaps,minimum_base_gap_mm=round(cell.val().distance(base.val()),3),pcb_gap_mm=round(cell.val().distance(parts['pcb_envelope'].val()),3)))
        if x!=144:
            bw,bh=SPEC['battery']['bay'][:2]
            fence=box(x-bw/2-1,y-bh/2-1,-16,bw+2,bh+2,16).cut(box(x-bw/2,y-bh/2,-17,bw,bh,20))
            fence=fence.intersect(plane_halfspace(inside=True)).intersect(plane_halfspace(False,True,6))
            fence=fence.cut(box(x-bw/2-2,y-3,floor_z(y,True)+2,5,6,10))
            variant=variant.union(fence)
    # Extra bay fences must also clear the board, components and all other envelopes.
    for name,part in parts.items():assert variant.intersect(part).val().Volume()<.001,name
    # Space for a shared pack protection board, including its insulation.
    pcm=box(49.5,46,-8.5,25,12,3)
    for part in [variant,*parts.values(),*pouches]:assert pcm.intersect(part).val().Volume()<.001
    pack=cq.Workplane('XY').newObject([cq.Compound.makeCompound([c.val() for c in pouches]+[pcm.val()])])
    assert variant.val().isValid() and variant.intersect(pack).val().Volume()<.001
    for name,part in [('case_base_three_bay',variant),('battery_pack_envelopes',pack)]:
        cq.exporters.export(part.mirror('XZ'),str(folder/(name+'.step')));normalize_text(folder/(name+'.step'))
    printable=variant.rotate((0,0,0),(1,0,0),-ANGLE).translate((0,0,-FLOOR_INTERCEPT*math.cos(math.radians(ANGLE))))
    cq.exporters.export(printable.mirror('XZ'),str(folder/'case_base_three_bay.stl'),tolerance=.05,angularTolerance=.15)
    current=json.loads((ROOT/'reports/electrical-analysis.json').read_text());daily=current['mixed_8h_active_16h_idle_nominal_days']
    report=dict(bays=bays,shared_pcm_envelope_mm=[25,12,3],shared_pcm_origin_mm=[49.5,46,-8.5],chemistry='Factory assembled protected 1S2P or 1S3P, 3.7 V nominal / 4.2 V full; one output to J1',
      options=[dict(pouches=n,nominal_capacity_mAh=n*1000,nominal_mixed_runtime_days=round(daily*n,1),ideal_100mA_charge_lower_bound_hours=n*10) for n in [1,2,3]],
      assumptions=['1000 mAh per pouch is a capacity target, not a verified cell model. Entire pouch including seams/wrapping/leads must fit the envelope.','Pack manufacturer must provide matched cells, protection and suitable branch fault protection; no parallel JST headers or DIY cell splicing.','Keep existing 100 mA charging setting; real charging exceeds the ideal bound because of load and CV taper.','Shared protection board and wiring envelopes require the selected pack drawing. Adhesive insulation must fit the measured remaining gap.','RF/EC noise and cell temperature need retesting with multiple conductive pouches.'],
      sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'case_base.step',folder/'components.step',ROOT/'design/yakb.json']})
    (ROOT/'reports/battery-study.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
