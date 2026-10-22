"""Generate the pinned YAKB ZMK integration; physical calibration is required."""
import csv
from common import ROOT, keys
from circuit import ASSIGN, PM_TO_NRF, PM_TO_PAD

def main():
    out=ROOT/'firmware/config/boards/shields/yakb';ks=keys()
    masks=[sum(1<<i for i in range(15) if i not in {k['col'] for k in ks if k['row']==r}) for r in range(5)]
    overlay='''/* YAKB A0 - engineering prototype; compiled for the pinned target; hardware calibration required. */
#include <dt-bindings/gpio/gpio.h>
#include <dt-bindings/adc/adc.h>
#include <zephyr/dt-bindings/adc/nrf-saadc.h>
#include <dt-bindings/zmk/matrix_transform.h>

/ {
    chosen { zmk,kscan = &kscan0; zmk,matrix-transform = &transform0; };
    mux0: mux0 {
        compatible = "zmk,gpio-mux";
        gpio-controller;
        #gpio-cells = <2>;
        select-gpios = <&pro_micro 5 GPIO_ACTIVE_HIGH>, <&pro_micro 6 GPIO_ACTIVE_HIGH>, <&pro_micro 7 GPIO_ACTIVE_HIGH>;
        en-gpios = <&pro_micro 8 GPIO_ACTIVE_LOW>;
    };
    mux1: mux1 {
        compatible = "zmk,gpio-mux";
        gpio-controller;
        #gpio-cells = <2>;
        select-gpios = <&pro_micro 5 GPIO_ACTIVE_HIGH>, <&pro_micro 6 GPIO_ACTIVE_HIGH>, <&pro_micro 7 GPIO_ACTIVE_HIGH>;
        en-gpios = <&pro_micro 9 GPIO_ACTIVE_LOW>;
    };
    transform0: transform0 {
        compatible = "zmk,matrix-transform";
        rows = <5>;
        columns = <15>;
        map = <
'''
    for row in range(5):overlay+='            '+' '.join(f"RC({k['row']},{k['col']})" for k in ks if k['row']==row)+'\n'
    overlay+='''        >;
    };
    kscan0: kscan0 {
        compatible = "zmk,kscan-ec-matrix";
        strobe-gpios = <&pro_micro 0 GPIO_ACTIVE_HIGH>, <&pro_micro 1 GPIO_ACTIVE_HIGH>,
                       <&pro_micro 2 GPIO_ACTIVE_HIGH>, <&pro_micro 3 GPIO_ACTIVE_HIGH>, <&pro_micro 4 GPIO_ACTIVE_HIGH>;
        input-gpios = '''+', '.join(f'<&mux{c//8} {c%8} GPIO_ACTIVE_HIGH>' for c in range(15))+''';
        drain-gpios = <&pro_micro 10 GPIO_ACTIVE_HIGH>;
        power-gpios = <&pro_micro 15 GPIO_ACTIVE_LOW>;
        io-channels = <&adc 0>;
        strobe-input-masks = <'''+ ' '.join(hex(m) for m in masks)+'''>;
        matrix-warm-up-us = <200>;
        matrix-relax-us = <10>;
        adc-read-settle-us = <5>;
        trigger-percentage = <50>;
        active-polling-interval-ms = <4>;
        idle-polling-interval-ms = <8>;
        sleep-polling-interval-ms = <12>;
        idle-after-secs = <5>;
        sleep-after-secs = <300>;
        dynamic-polling-interval;
    };
};

&adc {
    status = "okay";
    #address-cells = <1>;
    #size-cells = <0>;
    channel@0 {
        reg = <0>;
        zephyr,gain = "ADC_GAIN_1_6";
        zephyr,reference = "ADC_REF_INTERNAL";
        zephyr,acquisition-time = <ADC_ACQ_TIME(ADC_ACQ_TIME_MICROSECONDS, 10)>;
        zephyr,resolution = <12>;
        zephyr,input-positive = <NRF_SAADC_AIN0>; /* D19=P0.02. D18 is NOT an ADC pin on nice!nano! */
    };
};
&i2c0 { status = "disabled"; };
&spi1 { status = "disabled"; };
&uart0 { status = "disabled"; };
'''
    (out/'yakb.overlay').write_text(overlay)
    (out/'Kconfig.shield').write_text('config SHIELD_YAKB\n    def_bool $(shields_list_contains,yakb)\n')
    (out/'Kconfig.defconfig').write_text('if SHIELD_YAKB\nconfig ZMK_KEYBOARD_NAME\n    default "YAKB"\nendif\n')
    (out/'yakb.conf').write_text('''# Compiled integration; timings require oscilloscope/current profiling.
CONFIG_ADC=y
CONFIG_GPIO=y
CONFIG_ZMK_KSCAN_EC_MATRIX=y
CONFIG_ZMK_KSCAN_EC_MATRIX_SETTINGS=y
CONFIG_ZMK_KSCAN_EC_MATRIX_DYNAMIC_POLL_RATE=y
CONFIG_ZMK_KSCAN_EC_MATRIX_FAKE_OPEN_DRAIN=y
CONFIG_ZMK_KSCAN_EC_MATRIX_THREAD_PRIORITY=15
CONFIG_ASSERT=y
CONFIG_ZMK_BATTERY_REPORTING=y
CONFIG_ZMK_SLEEP=n
# EC wake needs periodic scans. Deep sleep is disabled until an independent wake path exists.
''')
    names={'Esc':'ESC','Tab':'TAB','Backspace':'BSPC','Control':'LCTRL','Enter':'RET','Shift':'LSHFT','RShift':'RSHFT','Fn':None,'LGUI':'LGUI','RGUI':'RGUI','LAlt':'LALT','RAlt':'RALT','Space':'SPACE','-':'MINUS','=':'EQUAL','\\':'BSLH','`':'GRAVE','[':'LBKT',']':'RBKT',';':'SEMI',"'":'SQT',',':'COMMA','.':'DOT','/':'FSLH'}
    def base(k):
        s=k['label'];return '&mo 1' if s=='Fn' else '&kp '+names.get(s,('N'+s) if s.isdigit() else s)
    def fn(k):
        s=k['label'];return {'1':'&bt BT_SEL 0','2':'&bt BT_SEL 1','3':'&bt BT_SEL 2','4':'&bt BT_CLR','5':'&out OUT_USB','6':'&out OUT_BLE','Backspace':'&kp DEL','H':'&kp LEFT','J':'&kp DOWN','K':'&kp UP','L':'&kp RIGHT','Esc':'&bootloader'}.get(s,'&trans')
    text='/* YAKB A0 keymap - engineering prototype */\n#include <behaviors.dtsi>\n#include <dt-bindings/zmk/keys.h>\n#include <dt-bindings/zmk/bt.h>\n#include <dt-bindings/zmk/outputs.h>\n/ { keymap { compatible = "zmk,keymap";\n'
    for layer,func in [('base',base),('fn',fn)]:
        text+=f'    {layer} {{ bindings = <\n'
        for row in range(5):text+='        '+' '.join(func(k) for k in ks if k['row']==row)+'\n'
        text+='    >; };\n'
    text+='}; };\n';(out/'yakb.keymap').write_text(text)
    with (ROOT/'design/pin-map.csv').open('w') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['Signal','Pro_Micro_D','nRF52840_pin','U1_pad'])
        for pm,signal in ASSIGN.items():w.writerow([signal,pm,PM_TO_NRF[pm],PM_TO_PAD[pm]])
    with (ROOT/'design/key-map.csv').open('w') as f:
        w=csv.DictWriter(f,lineterminator='\n',fieldnames=list(ks[0]));w.writeheader();w.writerows(ks)
    print('Generated 60-key transform, keymap, and masks:',[hex(m) for m in masks])

if __name__=='__main__':main()
