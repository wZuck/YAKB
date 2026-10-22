"""Check compiled EC channel allocation against the pinned battery driver."""
import re
from pathlib import Path


def check(workspace: Path, build: str):
    dts = (workspace / 'build' / build / 'zephyr/zephyr.dts').read_text()
    ec = re.search(r'kscan0: kscan0\s*\{(.*?)\n\s*\};', dts, re.S)[1]
    channel = int(re.search(r'io-channels\s*=\s*<\s*&adc\s+(0x[0-9a-f]+|\d+)', ec)[1], 0)
    node = re.search(r'channel@' + str(channel) + r'\s*\{(.*?)\n\s*\};', dts, re.S)[1]
    reg = int(re.search(r'\breg\s*=\s*<\s*(0x[0-9a-f]+|\d+)', node)[1], 0)
    positive = int(re.search(r'zephyr,input-positive\s*=\s*<\s*(0x[0-9a-f]+|\d+)', node)[1], 0)
    assert channel == reg == 1, 'EC must not overwrite battery logical channel 0'
    assert positive == 1, 'EC physical input must remain NRF_SAADC_AIN0 / P0.02'
    source = (workspace / 'zmk/app/module/drivers/sensor/battery/battery_nrf_vddh.c').read_text()
    assert '.channels = BIT(0)' in source
    acc = re.search(r'drv_data->acc = \(struct adc_channel_cfg\)\{(.*?)\};', source, re.S)[1]
    assert '.channel_id' not in acc, 'Re-audit changed battery driver channel allocation'
    assert '.input_positive = SAADC_CH_PSELN_PSELN_VDDHDIV5' in acc
    return dict(ec_logical_channel=channel, battery_logical_channel=0,
                ec_physical_input='AIN0/P0.02', battery_physical_input='VDDHDIV5')
