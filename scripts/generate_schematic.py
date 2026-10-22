"""Self-contained KiCad schematic with explicit, labelled pin connectivity.

Every pin comes from circuit.py. The block-style symbols show physical pin
numbers; amplifier polarity and MOSFET G/S/D are named explicitly.
"""
import uuid, json, itertools
from common import ROOT
from circuit import components, PM_TO_PAD, PM_TO_NRF, ASSIGN

_ids=itertools.count()
def uid():return str(uuid.uuid5(uuid.NAMESPACE_URL,"https://github.com/wZuck/YAKB/kicad/A0/"+str(next(_ids))))
def q(s):return json.dumps(str(s),ensure_ascii=False)
def fx(size=1):return f'(effects (font (size {size} {size})))'

def pin_names(c):
    if c['ref']=='U1':
        d={str(pin):f'D{pm}/{PM_TO_NRF[pm]}' for pm,pin in PM_TO_PAD.items()}
        d.update({'3':'GND','4':'GND','21':'VCC_3.3V','22':'RESET','23':'GND','24':'BATTERY+'});return d
    if c['ref'] in ['U2','U3']:
        return dict(zip(map(str,range(1,17)),['X4','X6','COM','X7','X5','INH','VEE','GND','C','B','A','X3','X0','X1','X2','VCC']))
    if c['ref']=='U4':return {'1':'NC','2':'IN-','3':'IN+','4':'V-','5':'NC','6':'OUT','7':'V+','8':'NC'}
    if c['ref']=='Q1':return {'1':'G','2':'S','3':'D'}
    if c['kind']=='EC':return {'1':'DRIVE','2':'SENSE','3':'GUARD'}
    return c['pins']

def main():
    root_id=uid();lib=[];body=[];placements={}
    core={'U1':(70,90),'U2':(235,90),'U3':(390,90),'U4':(545,90),'Q1':(675,90),'J1':(750,90),'SW1':(675,145),'SW2':(750,145)}
    for c in components():
        ref=c['ref'];kind=c['kind'];pins=sorted(c['pins'],key=int);names=pin_names(c)
        if ref in core:cx,cy=core[ref]
        elif kind=='EC':
            n=int(ref[2:])-1;cx=35+(n%15)*54;cy=385+(n//15)*46
        elif ref.startswith('R') and 10<=int(ref[1:])<=24:cx=35+(int(ref[1:])-10)*54;cy=270
        elif ref.startswith('R') and int(ref[1:])<10:cx=55+(int(ref[1:])-1)*70;cy=205
        elif ref.startswith('R'):cx=440+(int(ref[1:])-30)*54;cy=205
        else:cx=55+(int(ref[1:])-1)*120;cy=325
        cx=round(cx/1.27)*1.27;cy=round(cy/1.27)*1.27
        placements[ref]=(cx,cy)
        nleft=(len(pins)+1)//2; spacing=2.54
        h=max(5.08,(nleft+1)*spacing); halfw=20.32 if kind=='MODULE' else (12.7 if len(pins)>3 else 5.08)
        coords={}
        for index,pin in enumerate(pins):
            left=index<nleft;j=index if left else index-nleft
            ly=(nleft-1)*spacing/2-j*spacing
            coords[pin]=(-halfw-2.54 if left else halfw+2.54,ly,0 if left else 180)
        lname='YAKB:'+ref
        inbom='no' if kind=='EC' else 'yes'
        symbols=[f'(rectangle (start {-halfw} {-h/2}) (end {halfw} {h/2}) (stroke (width 0.254) (type default)) (fill (type background)))']
        ps=[]
        for pin,(px,py,ang) in coords.items():
            typ='passive'
            if ref=='U1':
                typ='power_out' if pin in ('21','3') else ('output' if c['pins'][pin].startswith(('ROW_DRV','MUX','AFE_ON')) else ('input' if c['pins'][pin]=='ADC' else 'passive'))
            elif ref in ['U2','U3']:typ='input' if pin in ['6','9','10','11'] else ('power_in' if pin in ['7','8','16'] else 'passive')
            elif ref=='U4':typ='input' if pin in ['2','3'] else ('output' if pin=='6' else ('power_in' if pin in ['4','7'] else 'no_connect'))
            elif ref=='Q1' and pin=='3':typ='power_out'
            ps.append(f'(pin {typ} line (at {px} {py} {ang}) (length 2.54) (name {q(names.get(pin,pin))} {fx(.9)}) (number {q(pin)} {fx(.9)}))')
        lib.append(f'(symbol {q(lname)} (pin_names (offset 0.8)) (in_bom {inbom}) (on_board yes) (property "Reference" "{ref}" (at 0 {h/2+2.54} 0) {fx()}) (property "Value" {q(c["value"])} (at 0 {-h/2-2.54} 0) {fx()}) (symbol {q(ref+"_0_1")} {"".join(symbols)}) (symbol {q(ref+"_1_1")} {"".join(ps)}))')
        instance=uid()
        body.append(f'(symbol (lib_id {q(lname)}) (at {cx} {cy} 0) (unit 1) (in_bom {inbom}) (on_board yes) (dnp no) (uuid {instance}) (property "Reference" {q(ref)} (at {cx} {cy-h/2-3} 0) {fx()}) (property "Value" {q(c["value"])} (at {cx} {cy+h/2+3} 0) {fx()}) (property "Footprint" {q(c["footprint"])} (at {cx} {cy} 0) (effects (font (size 1 1)) hide)) '+''.join(f'(pin {q(pin)} (uuid {uid()}))' for pin in pins)+f' (instances (project "YAKB" (path "/{root_id}" (reference {q(ref)}) (unit 1)))))')
        for pin,(px,py,ang) in coords.items():
            x,y=cx+px,cy-py;net=c['pins'][pin]
            if not net:
                body.append(f'(no_connect (at {x} {y}) (uuid {uid()}))');continue
            dx=-3.81 if px<0 else 3.81;end=x+dx
            body.append(f'(wire (pts (xy {x} {y}) (xy {end} {y})) (stroke (width 0) (type default)) (uuid {uid()}))')
            body.append(f'(global_label {q(net)} (shape bidirectional) (at {end} {y} {0 if px<0 else 180}) (effects (font (size 0.9 0.9)) (justify {"right" if px<0 else "left"} bottom)) (uuid {uid()}))')
    annotations=[(20,15,'YAKB A0 | NiZ EC + HHKB 6u + nice!nano v2 | ENGINEERING PROTOTYPE'),
                 (20,25,'Physical pin numbers and named nets are authoritative. USB is an external passive data extension to U1.'),
                 (20,35,'U2/U3: only one INH low at a time. U4 gain 101. DRAIN goes through R32 to SENSE. Q1 gates U4 only.'),
                 (20,45,'SW1/SW2 are 2.54mm solder-hole harnesses. No external 5V connection to U1 BATTERY+.'),
                 (20,355,'EC electrodes: logical row = physical row; column = floor(x_u + width_u/2), including empty column bins.')]
    for x,y,t in annotations:body.append(f'(text {q(t)} (at {x} {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid()}))')
    source=f'(kicad_sch (version 20250114) (generator "yakb") (uuid {root_id}) (paper "A1") (title_block (title "YAKB A0 - ENGINEERING DESIGN") (date "2026-10-22") (rev "A0 - NOT FOR FAB")) (lib_symbols {"".join(lib)}) {"".join(body)})\n'
    (ROOT/'hardware/YAKB.kicad_sch').write_text(source)
    library=''.join(s.replace('(symbol "YAKB:', '(symbol "',1) for s in lib)
    (ROOT/'hardware/YAKB.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "yakb") '+library+')\n')
    (ROOT/'hardware/sym-lib-table').write_text('(sym_lib_table (lib (name "YAKB")(type "KiCad")(uri "${KIPRJMOD}/YAKB.kicad_sym")(options "")(descr "YAKB physical pin block symbols")))\n')
    print('Generated schematic:',len(components()),'symbols')

if __name__=='__main__':main()
