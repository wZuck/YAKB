# Electrical integrity, interference and power budget

[简体中文](electrical-analysis.zh-CN.md) · [Calculated data](../reports/electrical-analysis.json) · [Battery options](battery-options.md)

USB HID and BLE HID are both enabled in both actual builds. Fn+5 selects USB, Fn+6 selects BLE, and Fn+1/2/3 selects BLE profiles. USB is initially preferred; manual selection persists. One endpoint receives reports at a time. USB data works with the battery disconnected; select BLE to type wirelessly while USB powers the board. The battery switch must be on for charging. [ZMK output behavior](https://zmk.dev/docs/keymaps/behaviors/outputs)

## Signal integrity

The original `SN74HC4051D` reference did not match the cited TI part. The BOM now specifies active SOIC-16 **CD74HC4051M96**, preserving the pin map and footprint. Do not substitute HCT/CD4051B without review. [TI ordering page](https://www.ti.com/product/CD74HC4051/part-details/CD74HC4051M96), [datasheet](https://www.ti.com/lit/ds/symlink/cd74hc4051.pdf)

Native routed segment totals are SENSE **162.105 mm**, ADC **58.656 mm**, FB **21.034 mm**, AFE supply **25.215 mm**. These include branches; they are neither point-to-point distances nor extracted impedance. The long high-impedance SENSE net is the main remaining analog risk: parasitic capacitance reduces signal and digital/RF coupling can produce false input. ADC has a low-impedance amplifier driver; the feedback loop remains sensitive. If measured margin is inadequate, cluster muxes, feedback parts and C4 and reroute before merely lowering thresholds.

The gain is 101. SAADC uses 12 bits, a 0.6 V internal reference and 1/6 gain: nominal 3.6 V range, 0.879 mV/LSB, about 8.70 µV referred to the amplifier input. These values do not specify effective resolution. Real signal swing, amplifier saturation and noise determine usable margin.

Each point waits 10 µs for discharge, 5 µs before conversion and uses 10 µs acquisition; amplifier warm-up is 200 µs/frame. R32×C4 alone is 0.22 µs, but actual total capacitance also includes muxes, traces and electrodes. That isolated RC value cannot certify settling. Row series resistors, exclusive mux selection, grounded unused channel and inner-layer sensor keepouts reduce specific coupling paths. They do not eliminate crosstalk.

The board deliberately lacks continuous planes beneath sensing cells. The GND routed-segment sum of about 2458 mm describes the entire branched net, not a single return wire. Sparse returns and local decoupling need testing under USB charging, digital switching and radio activity. OPA350's 38 MHz bandwidth does not guarantee stability in this layout. Its typical quiescent current is about 5.2 mA, with a 7.5 mA maximum at 25°C; repeated power-up settling must be measured. [OPA350 datasheet](https://www.ti.com/lit/ds/symlink/opa350.pdf)

Readout uses short critical sections, not explicit synchronization with BLE slots. Host logic tests do not model SAADC interrupts or radio preemption. Measure complete frame time, first presses and releases under radio traffic. The reviewed driver fixes invalid calibration, zero-noise division and thread priority; see the [fix record](review-fixes.md).

## RF and USB

The right-facing antenna has an all-copper-layer keepout at x=268…285, y=79…91 mm. The plate previously covered that projection, a potential obstruction with metal. A **21×16 mm** window under the right blocker now clears it; actual STEP intersection with the keepout projection is zero. Prefer copper-free FR4/G10 and a plastic case; retain the window with a metal plate.

This is geometric mitigation, not RF certification. Metal cases, shielded USB cable, pouch foil, inserts and hands can still detune the antenna. Keep wires and foil out of its volume. Multiple pouches require renewed RF and EC tests. Nearby 2.4 GHz Wi-Fi and USB3 equipment can cause retransmissions and increase average current.

USB data stays inside the controller and a complete USB 2.0 data extension, rather than crossing the sensing PCB. Preserve cable shielding and strain relief. A charge-only lead or ad-hoc bare-wire extension is unsuitable. [nice!nano documentation](https://nicekeyboards.com/docs/nice-nano/)

Compare bare board, closed case, installed USB extension and multi-pouch pack at 1/3/5 m and normal desk positions with nearby Wi-Fi traffic. Record RSSI, disconnects, missing input and release events. Geometry cannot guarantee wireless range.

## Unmeasured current scenarios

Fixed busy waits alone total `0.2 + 60×(0.010+0.005) = 1.1 ms/frame`; ADC acquisition adds 0.6 ms before conversion/GPIO/mux/scheduler overhead. Poll waits of 4/8/12 ms therefore are not whole-frame periods.

Scenarios use 2/3/6 ms frames, 8.2/8.7/13.5 mA during scanning and 0.1/0.25/0.6 mA background. Scanning includes MCU plus amplifier; background includes retained supply, average BLE and board consumption. Nordic describes why workload matters; a radio peak is not an average keyboard current. [Nordic current consumption](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/chapters/current_consumption/doc/frontpage.html)

The first-order battery-current budget approximates VCC input/output current as equal; actual regulation efficiency, temperature and radio duty require measurement. It includes conservative full charging of the switched 100 nF capacitor each frame:

`Iavg = Ibackground + Iactive*tframe/(tframe+twait) + 0.1µF*3.3V/(tframe+twait)`

| State | Wait | Scenario range | Central estimate | Central runtime, 1000 mAh / 80% usable |
| --- | --- | --- | --- | --- |
| Active | 4 ms | 2.89–8.73 mA | 4.03 mA | 199 h / 8.3 days continuous |
| Idle | 8 ms | 1.77–6.41 mA | 2.65 mA | 302 h / 12.6 days |
| Long idle | 12 ms | 1.30–5.12 mA | 2.01 mA | 398 h / 16.6 days |

Eight active hours and sixteen long-idle hours per day gives about **12.4 days per 1000 mAh** centrally. 500 mAh halves it; 2000/3000 mAh doubles/triples it only if current is unchanged. These are scenarios, not guaranteed bounds; frames above 6 ms or frequent retries can exceed them. Deep sleep remains disabled, so months of standby are not claimed.

At the default approximately 100 mA charge current, ideal constant-current lower bounds for 1000/2000/3000 mAh are 10/20/30 hours. Real charging takes longer due to taper and operating load. Increasing charge current requires cell, protection, wiring and temperature review. [nice!nano FAQ](https://nicekeyboards.com/docs/nice-nano/faq/)

## First-article acceptance

Record rails, ripple, SENSE/ADC and per-key released/pressed distributions under direct USB, extended USB, charging plus BLE and battery BLE. Use at least 1000 samples per condition and note probe loading. A pressed/released difference at least ten times peak-to-peak noise is an initial engineering target, not a guaranteed specification. Check farthest cells, neighboring changes, chords, slow releases, power-up, long-idle first taps and radio contention across battery voltage and temperature.

Measure battery-side average/peak current for activity, idle, long idle, reconnect and physical-off states. Replace model assumptions with those measurements. Validate charging temperature and protection-board self-consumption, especially with a larger pack. No electrical-noise, EMC, RF-range or runtime certification has yet been performed.

EC uses SAADC logical channel1 with physical AIN0/P0.02 unchanged; logical0 is reserved for the ZMK battery driver VDDHDIV5 input. The previous shared logical0 allocation overwrote channel configuration. The fix includes regression checks for both initialization orders.
