"""Native PCB and fabrication checks for defects that ERC/DRC do not cover."""
import hashlib,json,re
import pcbnew as p,wx
from common import ROOT,SPEC
from generate_pcb import hole_layers

def main():
    app=wx.App(False)
    assert not p.LSET.AllCuMask().Contains(p.F_Mask)
    test=hole_layers()
    assert test.Contains(p.F_Mask) and test.Contains(p.B_Mask)
    assert not p.LSET.AllCuMask().Contains(p.F_Mask),'Shared copper mask was mutated'
    board=ROOT/'hardware/YAKB.kicad_pcb';b=p.LoadBoard(str(board));footprints={f.GetReference():f for f in b.GetFootprints()}
    pth=[];models=[]
    for ref,f in footprints.items():
        if f.Models():models.append(ref)
        for a in f.Pads():
            if a.GetAttribute()==p.PAD_ATTRIB_PTH:
                assert a.IsOnLayer(p.F_Mask) and a.IsOnLayer(p.B_Mask),(ref,a.GetNumber(),'covered annulus')
                pth.append((ref,a.GetNumber()))
            if ref.startswith('EC'):
                assert not a.IsOnLayer(p.F_Mask) and not a.IsOnLayer(p.B_Mask),(ref,'exposed sensor')
                assert not a.IsOnLayer(p.F_Paste) and not a.IsOnLayer(p.B_Paste)
    assert len(pth)==30
    u=footprints['U1'];pads={a.GetNumber():a for a in u.Pads()};center=p.ToMM(u.GetPosition().x)
    assert all(p.ToMM(pads[n].GetPosition().x)<center for n in ['1','24']),'USB end must be on the left'
    assert abs(u.GetOrientationDegrees()-SPEC['module']['pcb_rotation_deg'])<1e-5
    native_pads={(f.GetReference(),a.GetNumber(),a.GetLayer()):a for f in b.GetFootprints() for a in f.Pads()}
    for f in json.loads((ROOT/'design/pad-map.json').read_text()):
        expected=footprints[f['ref']]
        assert abs(f['x']-p.ToMM(expected.GetPosition().x))<1e-6
        for a in f['pads']:
            assert any(n.GetNumber()==a['number'] and abs(a['x']-p.ToMM(n.GetPosition().x))<1e-6 and abs(a['y']-p.ToMM(n.GetPosition().y))<1e-6 for n in expected.Pads())
    gerbers={}
    for side,suffix in [('F','gts'),('B','gbs')]:
        source=(ROOT/f'fabrication/gerbers/YAKB-{side}_Mask.{suffix}').read_text();ref=None;counts={}
        for line in source.splitlines():
            m=re.match(r'%TO.C,([^*]+)\*%',line)
            if m:ref=m[1]
            if line.startswith('%TD'):ref=None
            if ref and re.search(r'D03\*$',line):counts[ref]=counts.get(ref,0)+1
        for ref,count in [('U1',24),('J1',2),('SW1',2),('SW2',2)]:assert counts.get(ref)==count,(side,ref,counts.get(ref))
        gerbers[side]=counts
    scene=json.loads((ROOT/'design/pcb-scene.json').read_text());digest=hashlib.sha256(board.read_bytes()).hexdigest();assert scene['pcb_sha256']==digest
    component_report=json.loads((ROOT/'reports/component-geometry.json').read_text());assert component_report['pcb_sha256']==digest
    report=dict(pcb_sha256=digest,plated_pads_with_two_sided_mask_openings=len(pth),sensor_copper_masked=True,shared_mask_unmodified=True,usb_points_left=True,library_component_models=len(models),unmodelled_populated_positions=sorted(r for r in footprints if not r.startswith(('EC','H_')) and r not in models),gerber_pth_openings={'front':30,'back':30},native_pad_map_matches=True,limitations=['NiZ and mating cable/socket samples require physical measurement.'])
    assert report['unmodelled_populated_positions']==['SW1','SW2','U1']
    (ROOT/'reports/hardware-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
