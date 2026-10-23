"""B1 first-order estimates from saved native flex traces; not EMC or power measurements."""
import json,math,hashlib
import pcbnew as p,wx
from common import ROOT

def main():
 app=wx.App(False);file='hardware/modular/YAKB-shaped-FPC-B1.kicad_pcb';b=p.LoadBoard(str(ROOT/file));lengths={}
 for t in b.GetTracks():lengths[t.GetNetname()]=lengths.get(t.GetNetname(),0)+p.ToMM(t.GetLength())
 assert len(lengths)==24
 length=max(lengths.values())/1000;resistance=.01724*length/(.15*.035);loop=resistance/2+resistance/7;tau=(47+resistance)*1e-9
 report=dict(status='unmeasured engineering estimates; equal-return-current assumption',native_conductor_lengths_mm=lengths,copper_resistivity_ohm_mm2_per_m=.01724,nominal_cross_section_mm2=.15*.035,max_conductor_resistance_ohm=resistance,battery_loop_ohm_ideal=loop,charge_current_A=.1,charge_loop_drop_V=.1*loop,charge_loop_loss_W=.1**2*loop,charge_ground_offset_V_ideal=.1*resistance/7,ADC_filter_time_constant_s=tau,ADC_ideal_full_step_half_LSB_settle_s=tau*math.log(8192),ADC_ideal_cutoff_Hz=1/(2*math.pi*tau),assumed_extra_digital_current_A=[12*c*1e-12*3.3*5000 for c in [10,100]],assumptions=['35um copper and 0.15mm traces; contact/pin/rigid trace resistance excluded.','Ground current is assumed equal across seven conductors; real sharing and switching loops differ.','Capacitive load 10..100pF per twelve digital lines and effective 5kHz charging are hypothetical.','RC settling excludes amplifier/distributed cable behaviour and interrupt scheduling.','No RF/EMC simulation, charge-temperature, analog-noise or runtime measurements.'])
 report['assumed_ADC_filter_full_swing_current_A']=1e-9*3.3*60/.007
 baseline=json.loads((ROOT/'reports/electrical-analysis.json').read_text());activity=baseline['scenarios']['active']['nominal_current_mA']/1000
 report['assumed_activity_current_A']=[activity+report['assumed_ADC_filter_full_swing_current_A']+i for i in report['assumed_extra_digital_current_A']]
 report['assumed_1000mAh_80pct_activity_hours']=[.8/i for i in report['assumed_activity_current_A']]
 report['sources']={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in [file,'design/modular.json','scripts/analyze_modular.py','reports/electrical-analysis.json']}
 (ROOT/'reports/modular-electrical.json').write_text(json.dumps(report,indent=2)+'\n');print('Native FPC length %.3f mm; ideal 100mA loop drop %.1f mV; ground offset %.1f mV; unmeasured.'%(length*1000,.1*loop*1000,.1*resistance/7*1000))
if __name__=='__main__':main()
