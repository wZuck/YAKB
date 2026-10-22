"""Cross-file checks; does not substitute for DRC, measurements or firmware build."""
import json, csv, math, re, hashlib
import xml.etree.ElementTree as ET
from common import ROOT, SPEC, keys
from circuit import components, ASSIGN, PM_TO_NRF

def main():
    ks=keys();cs=components();assert len(ks)==60
    assert [sum(k['row']==r for k in ks) for r in range(5)]==[15,14,13,13,5]
    assert len({(k['row'],k['col']) for k in ks})==60
    assert next(k for k in ks if k['label']=='Space')['width']==6
    for k in ks:
        assert k['x']-7>0 and k['x']+7<SPEC['pcb']['width']
        assert k['y']-7>0 and k['y']+7<SPEC['pcb']['height']
    # Import the actual netlist emitted by KiCad, not the generator's own output.
    r=ET.parse(ROOT/'reports/schematic.net.xml').getroot();actual={}
    for net in r.findall('./nets/net'):
        name=net.attrib['name'].lstrip('/')
        if name.startswith('unconnected-'):continue
        for n in net.findall('node'):actual[(n.attrib['ref'],n.attrib['pin'])]=name
    expected={(c['ref'],pin):net for c in cs for pin,net in c['pins'].items() if net}
    assert actual==expected,dict(missing=set(expected.items())-set(actual.items()),extra=set(actual.items())-set(expected.items()))
    pcb=json.loads((ROOT/'reports/pcb-connectivity.json').read_text())
    assert {(a['ref'],a['pin']):a['net'] for a in pcb['pins']}==expected
    assert pcb['copper_layers']==SPEC['pcb']['copper_layers']==4
    drc=json.loads((ROOT/'reports/drc.json').read_text())
    assert not drc['violations'] and not drc['unconnected_items'] and not drc.get('schematic_parity',[])
    erc=json.loads((ROOT/'reports/erc.json').read_text())
    assert not any(s['violations'] for s in erc['sheets'])
    overlay=(ROOT/'firmware/config/boards/shields/yakb/yakb.overlay').read_text()
    positions=[tuple(map(int,m)) for m in re.findall(r'RC\((\d+),(\d+)\)',overlay)]
    assert positions==[(k['row'],k['col']) for k in ks]
    assert 'NRF_SAADC_AIN0' in overlay and ASSIGN[19]=='ADC' and PM_TO_NRF[19]=='P0.02/AIN0'
    assert 'GPIO_ACTIVE_LOW' in overlay
    assert 'CONFIG_ZMK_SLEEP=n' in (ROOT/'firmware/config/boards/shields/yakb/yakb.conf').read_text()
    m=json.loads((ROOT/'reports/mechanical.json').read_text())
    assert all(v<.01 for v in m['envelope_intersections_mm3'].values())
    # Mounts may occupy the space between housings; this only certifies electrode
    # disk clearance, and deliberately makes no housing/body clearance claim.
    disk_clearance=[]
    for hole in SPEC['mounts']:
        if hole['name']=='lower_left':continue
        nearest=min(math.hypot(max(abs(k['x']-hole['x'])-(hole['width']-hole['height'])/2,0),k['y']-hole['y'])-7-hole['height']/2 for k in ks)
        disk_clearance.append({'mount':hole['name'],'radius7_disk_to_capsule_edge_gap_mm':round(nearest,3)})
        assert nearest>0
    out={'name':'YAKB - Yet Another KeyBoard','key_count':60,'row_counts':[15,14,13,13,5],
         'components':len(cs),'physical_components_excluding_electrodes':len(cs)-60,
         'schematic_pins_checked':len(actual),'schematic_matches_design':True,
         'pcb_pins_match_schematic':True,'copper_layers':4,'drc_errors_warnings':0,'unconnected':0,'erc_errors_warnings':0,
         'pcb_sha256':hashlib.sha256((ROOT/'hardware/YAKB.kicad_pcb').read_bytes()).hexdigest(),
         'firmware_transform_matches_layout':True,'mechanical_envelopes_clear':True,
         'electrode_mount_gaps':disk_clearance,
         'limitations':['No physical NiZ/plate/stabilizer/case fit verified.','Continuity and noise require a built PCB.','Cross-file checks do not prove analog performance.']}
    (ROOT/'reports/design-checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
