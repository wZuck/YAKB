"""Trace-derived electrical review and explicit, unmeasured battery-current scenarios."""
import hashlib,json,math
import cadquery as cq
from common import ROOT,SPEC


def main():
    routing=json.loads((ROOT/'design/routing.json').read_text());lengths={}
    for item in routing['tracks']:
        if not item.get('via'):lengths[item['net']]=lengths.get(item['net'],0)+math.dist(item['a'],item['b'])
    # Conservative rectangular projection of the actual all-layer RF keepout.
    x,y,x2,y2=SPEC['module']['antenna_keepout'];w,h=x2-x,y2-y
    rf=cq.Workplane('XY').box(w,h,3,centered=(False,False,False)).translate((x,y,5)).val()
    plate=cq.importers.importStep(str(ROOT/'mechanical/plate_case.step')).val()
    overlap=plate.intersect(rf).Volume();assert overlap<.001
    scenarios={}
    for label,wait in [('active',4),('idle',8),('long_idle',12)]:
        def current(frame,active,background):return background+active*frame/(frame+wait)+.1*3.3/(frame+wait)
        low=current(2,8.2,.1);nom=current(3,8.7,.25);high=current(6,13.5,.6)
        scenarios[label]=dict(wait_ms=wait,current_mA=[round(low,3),round(nom,3),round(high,3)],runtime_1000mAh_80pct_hours=[round(800/high,1),round(800/nom,1),round(800/low,1)])
    mixed=(scenarios['active']['current_mA'][1]*8+scenarios['long_idle']['current_mA'][1]*16)/24
    result=dict(pcb_sha256=hashlib.sha256((ROOT/'hardware/YAKB.kicad_pcb').read_bytes()).hexdigest(),measured=False,
      trace_length_mm={key:round(lengths[key],3) for key in ['SENSE','ADC','FB','AFE_3V3','VCC','GND','MUX_A','MUX_B','MUX_C']},
      note='Lengths sum routed segments including branches; not point-to-point distances, extracted capacitance or impedance.',
      gain=101,adc_lsb_mV=3.6/4096*1000,input_referred_lsb_uV=3.6/4096/101*1e6,
      fixed_busy_wait_lower_bound_ms=.2+60*(.010+.005),adc_acquisition_only_addition_ms=60*.010,
      rf_plate_overlap_mm3=round(overlap,6),scenarios=scenarios,mixed_8h_active_16h_idle_nominal_days=round(800/mixed/24,1),
      model=dict(scan_frame_ms=[2,3,6],active_total_mA=[8.2,8.7,13.5],background_mA=[.1,.25,.6],switched_cap_uF=.1,battery_capacity_mAh=1000,usable_fraction=.8,
        equation='I = Ibackground + Iactive*tframe/(tframe+twait) + Cswitched[uF]*3.3/(tframe+twait)[ms]',
        limitations=['First-order battery-current budget, assuming approximate unity input/output current for gated VCC; regulator losses and radio duty require measurement.','The 2..6 ms frame and current ranges are scenarios, not guaranteed bounds.','No deep sleep or months-long standby claim.']),
      risks=['162 mm class branched SENSE net: board parasitic capacitance and digital coupling remain unmeasured.','Sparse ground routing instead of continuous planes: return impedance and charging noise need oscilloscope tests.','GPIO/ADC critical sections may delay BLE servicing; test under radio traffic.','RF window removes metal directly over antenna only; metal cases, cables, cell foil and hands can still detune it.'])
    (ROOT/'reports/electrical-analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
