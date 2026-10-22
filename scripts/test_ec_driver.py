"""Compile and exercise the actual patched EC read/poll functions with mocked ADC.

This tests event timing/filtering, not physical ADC settling or BLE latency.
"""
import argparse, hashlib, json, re, subprocess, tempfile
from pathlib import Path
from common import ROOT
from verify_adc_allocation import check as check_adc_allocation

def function(source,name):
    hit=re.search(r'(?:static )?(?:void|int|uint16_t|struct sample_results) '+name+r'\([^;]+?\)\s*\{',source)
    assert hit,name
    end=hit.end();depth=1
    while depth:
        depth += (source[end]=='{')-(source[end]=='}');end+=1
    return source[hit.start():end]


def test_adc_allocation(workspace):
    allocation=check_adc_allocation(workspace,'yakb')
    assert check_adc_allocation(workspace,'yakb-calibrator')==allocation
    battery=(workspace/'zmk/app/module/drivers/sensor/battery/battery_nrf_vddh.c').read_text()
    header=r'''
#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#define BIT(n) (1U<<(n))
#define CONFIG_ADC_NRFX_SAADC 1
#define ADC_GAIN_1_2 2
#define ADC_REF_INTERNAL 0
#define ADC_ACQ_TIME_MICROSECONDS 0
#define ADC_ACQ_TIME(unit,n) (n)
#define SAADC_CH_PSELN_PSELN_VDDHDIV5 99
#define LOG_ERR(...) ((void)0)
#define LOG_DBG(...) ((void)0)
struct device {void *data;};
struct adc_channel_cfg {int channel_id,gain,reference,acquisition_time,input_positive;};
struct adc_sequence {unsigned channels;void *buffer;unsigned buffer_size;int oversampling,calibrate,resolution;};
struct battery_value {int16_t adc_raw;};
struct vddh_data {struct adc_channel_cfg acc;struct adc_sequence as;struct battery_value value;};
static const struct device adc_dev={0};
static const struct device *adc=&adc_dev;
static int configured[8];
static bool device_is_ready(const struct device*d){return true;}
static int adc_channel_setup(const struct device*d,const struct adc_channel_cfg*c){assert(c->channel_id>=0&&c->channel_id<8);configured[c->channel_id]=c->input_positive;return 0;}
'''
    code=header+function(battery,'vddh_init')+r'''
static bool independent(int ec_channel,int battery_first){
 for(int i=0;i<8;i++)configured[i]=-1;
 struct vddh_data data={0};struct device dev={.data=&data};
 struct adc_channel_cfg ec={.channel_id=ec_channel,.input_positive=1};
 if(battery_first){assert(vddh_init(&dev)==0);adc_channel_setup(adc,&ec);}
 else {adc_channel_setup(adc,&ec);assert(vddh_init(&dev)==0);}
 assert(data.as.channels==BIT(0));
 return configured[0]==SAADC_CH_PSELN_PSELN_VDDHDIV5&&configured[ec_channel]==1;
}
int main(void){
 for(int order=0;order<2;order++){
  assert(independent(EC_CHANNEL,order));
  assert(!independent(0,order)); /* Old allocation must reproduce the collision. */
 }
 puts("Actual battery initializer: distinct EC input in both init orders; old channel 0 collision reproduced: PASS");
}
'''
    with tempfile.TemporaryDirectory(prefix='yakb-adc-test-') as temp:
        c=Path(temp)/'test.c';exe=Path(temp)/'test';c.write_text(code)
        subprocess.run(['cc','-std=c11','-DEC_CHANNEL='+str(allocation['ec_logical_channel']),str(c),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
    return allocation


def test_constant_adc(workspace, source):
    native_header=(workspace/'ec-support-zmk-module/drivers/kscan/zmk_kscan_ec_matrix.h').read_text().split('typedef')[0]
    header=r"""
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define BIT(x) (1ULL << (x))
#define LOG_DBG(...) ((void)0)
#define LOG_WRN(...) ((void)0)
#define K_MSEC(x) (x)
#define SAMPLE_COUNT 20
"""+native_header+r"""
struct gpio_dt_spec { void *port; };
struct device { void *data; const void *config; };
struct kscan_ec_matrix_config {
 int strobes_len,inputs_len; uint64_t *strobe_input_masks;
 struct gpio_dt_spec power; int matrix_warm_up_us;
 struct {int resolution;} adc_channel;
};
struct kscan_ec_matrix_data {
 void (*calibration_callback)(const struct zmk_kscan_ec_matrix_calibration_event *,const void *);
 const void *calibration_user_data;
};
struct sample_results {uint16_t min,max,avg,noise;};
static struct zmk_kscan_ec_matrix_calibration_entry cal;
static int high,completed,sleeps;
static struct zmk_kscan_ec_matrix_calibration_entry *calibration_entry_for_strobe_input(const struct device*d,int s,int i){return &cal;}
static uint16_t read_raw_matrix_state(const struct device*d,int s,int i){return high?3000:100;}
static void gpio_pin_set_dt(const struct gpio_dt_spec*p,int v){}
static void k_busy_wait(int t){}
static void k_sleep(int t){assert(++sleeps<100);}
static void callback(const struct zmk_kscan_ec_matrix_calibration_event*ev,const void*data){
 if(ev->type==CALIBRATION_EV_HIGH_SAMPLING_START)high=1;
 if(ev->type==CALIBRATION_EV_POSITION_COMPLETE){assert(ev->data.position_complete.snr==2901);completed++;}
}
"""
    code=header+function(source,'sample')+function(source,'calibrate')+r"""
int main(void){
 uint64_t masks[1]={0};struct kscan_ec_matrix_config cfg={.strobes_len=1,.inputs_len=1,.strobe_input_masks=masks,.adc_channel={12}};
 struct kscan_ec_matrix_data data={.calibration_callback=callback};struct device dev={&data,&cfg};
 calibrate(&dev);assert(completed==1&&cal.avg_low==100&&cal.avg_high==3000&&cal.noise==0);
 assert(data.calibration_callback==NULL);puts("constant-ADC calibration / zero-noise SNR: PASS");return 0;
}
"""
    with tempfile.TemporaryDirectory(prefix='yakb-calibration-test-') as temp:
        c=Path(temp)/'test.c';exe=Path(temp)/'test';c.write_text(code)
        subprocess.run(['cc','-std=c11','-fsanitize=undefined','-fno-sanitize-recover=all',str(c),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',type=Path,required=True);args=p.parse_args()
    driver=args.workspace/'ec-support-zmk-module/drivers/kscan/zmk_kscan_ec_matrix.c';source=driver.read_text()
    header=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#define CONFIG_ZMK_KSCAN_EC_MATRIX_DYNAMIC_POLL_RATE 1
#define IS_ENABLED(x) (x)
#define LOG_DBG(...) ((void)0)
#define LOG_WRN(...) ((void)0)
#define BIT(x) (1ULL << (x))
#define WRITE_BIT(v,b,on) ((v) = ((v) & ~BIT(b)) | ((on) ? BIT(b) : 0))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
struct gpio_dt_spec { void *port; };
struct device { void *data; const void *config; };
struct zmk_kscan_ec_matrix_calibration_entry { uint16_t avg_low, avg_high, noise; };
struct kscan_ec_matrix_config {
 int strobes_len,inputs_len; struct gpio_dt_spec power; uint32_t matrix_warm_up_us,trigger_percentage;
 uint64_t *strobe_input_masks; uint32_t active_polling_interval_ms,idle_polling_interval_ms,sleep_polling_interval_ms,idle_after_secs,sleep_after_secs;
};
struct kscan_ec_matrix_data {
 uint64_t matrix_state[5],reported_matrix_state[5]; const struct device *dev;
 void (*callback)(const struct device *,int,int,bool); uint32_t last_key_released_at,poll_interval;
};
static uint32_t now,press_time; static uint64_t raw[5];static int downs,ups;
static struct zmk_kscan_ec_matrix_calibration_entry cal={100,1100,2};
static struct zmk_kscan_ec_matrix_calibration_entry *calibration_entry_for_strobe_input(const struct device *d,int s,int r){return &cal;}
static uint16_t read_raw_matrix_state(const struct device *d,int s,int r){return (raw[s]&BIT(r))?1100:100;}
static void gpio_pin_set_dt(const struct gpio_dt_spec *p,int v){}
static void k_busy_wait(uint32_t t){}
static void k_yield(void){}
static uint32_t k_uptime_get(void){return now;}
static void event(const struct device *dev,int s,int r,bool pressed){if(pressed){downs++;press_time=now;}else ups++;}
'''
    routines='\n'.join(function(source,name) for name in ['normalize','kscan_ec_matrix_read','kscan_ec_matrix_update_poll_interval'])
    tests=r'''
int main(void){
 uint64_t masks[5]={0,2,0x4002,0x1001,0x6b73};
 struct kscan_ec_matrix_config cfg={.strobes_len=5,.inputs_len=15,.trigger_percentage=50,.strobe_input_masks=masks,.active_polling_interval_ms=4,.idle_polling_interval_ms=8,.sleep_polling_interval_ms=12,.idle_after_secs=5,.sleep_after_secs=300};
 struct kscan_ec_matrix_data data;struct device dev={.config=&cfg,.data=&data};int cases=0;
 for(int frame=0;frame<=6;frame+=2)for(int duration=40;duration<=150;duration+=10)for(int phase=0;phase<20;phase++){
  memset(&data,0,sizeof data);memset(raw,0,sizeof raw);data.dev=&dev;data.callback=event;data.last_key_released_at=1;data.poll_interval=12;downs=ups=0;
  uint32_t start=301001+phase;
  for(now=301001;now<start+duration+80;){
   raw[0]=(now>=start&&now<start+duration)?1:0;
   kscan_ec_matrix_read(&dev);kscan_ec_matrix_update_poll_interval(&dev);now+=frame+data.poll_interval;
  }
  assert(downs==1&&ups==1);assert(press_time-start<=28);cases++;
 }
 memset(&data,0,sizeof data);data.dev=&dev;data.callback=event;data.last_key_released_at=1;memset(raw,0,sizeof raw);now=400000;raw[0]=1;
 kscan_ec_matrix_read(&dev);kscan_ec_matrix_update_poll_interval(&dev);assert(data.poll_interval==4);
 raw[0]=0;now+=4;kscan_ec_matrix_read(&dev);kscan_ec_matrix_update_poll_interval(&dev);assert(data.last_key_released_at==now);
 now+=6000;kscan_ec_matrix_update_poll_interval(&dev);assert(data.poll_interval==8);
 now+=300000;kscan_ec_matrix_update_poll_interval(&dev);assert(data.poll_interval==12);
 memset(&data,0,sizeof data);data.dev=&dev;data.callback=event;downs=ups=0;
 for(int i=0;i<5;i++)raw[i]=0x7fff;
 kscan_ec_matrix_read(&dev);kscan_ec_matrix_read(&dev);assert(downs==60);
 memset(raw,0,sizeof raw);kscan_ec_matrix_read(&dev);assert(ups==60);
 assert(normalize(500,500,500)==0);assert(normalize(500,700,200)==0);
 memset(&data,0,sizeof data);data.dev=&dev;data.callback=event;downs=ups=0;
 cal.avg_low=cal.avg_high=500;raw[0]=1;kscan_ec_matrix_read(&dev);kscan_ec_matrix_read(&dev);assert(downs==0);
 printf("%d first-key phase/frame scenarios; transient idle recovery; 60-key mask/NKRO/release; invalid calibration: PASS\n",cases);
 return 0;
}
'''
    with tempfile.TemporaryDirectory(prefix='yakb-driver-test-') as temp:
        c=Path(temp)/'driver.c';exe=Path(temp)/'driver-test';c.write_text(header+routines+tests)
        subprocess.run(['cc','-std=c11','-O2',str(c),'-o',str(exe)],check=True)
        result=subprocess.run([str(exe)],check=True,capture_output=True,text=True)
    test_constant_adc(args.workspace,source)
    allocation=test_adc_allocation(args.workspace)
    conf=(args.workspace/'build/yakb/zephyr/.config').read_text()
    value=lambda n:int(re.search(r'^'+n+r'=(-?\d+)$',conf,re.M)[1])
    priority=value('CONFIG_ZMK_KSCAN_EC_MATRIX_THREAD_PRIORITY');coop=value('CONFIG_NUM_COOP_PRIORITIES');actual=-(coop-priority)
    assert -coop<=actual<0 and 'CONFIG_ASSERT=y' in conf
    report=dict(result=result.stdout.strip(),phase_frame_cases=960,constant_adc_calibration_passed=True,maximum_modelled_first_press_latency_ms=28,frame_overhead_range_ms=[0,6],cooperative_priority=actual,assertions_enabled=True,driver_sha256=hashlib.sha256(driver.read_bytes()).hexdigest(),limitations=['ADC mocked; no physical sampling, BLE timing or current measurement.'])
    report.update(adc_allocation=allocation,battery_init_order_regression_passed=True)
    (ROOT/'reports/firmware-regression.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout,report)

if __name__=='__main__':main()
