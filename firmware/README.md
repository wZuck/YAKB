# YAKB ZMK firmware

[简体中文](README.zh-CN.md) · [Build reproduction](../docs/reproduce.md)

The target is **nice!nano v2 / nRF52840**. `prebuilt/yakb-a0.uf2` is the normal keyboard image; `yakb-a0-calibrator.uf2` enables the USB CDC calibration shell. Both compiled successfully and remain untested on hardware. Hashes are in `prebuilt/SHA256SUMS`.

Top-level revisions are pinned in `config/west.yml`; `west-lock.yml` freezes all actual dependencies. The matrix has 5 rows, 15 inputs and 60 valid positions, with masks `0x0 0x2 0x4002 0x1001 0x6b73`.

1. Disconnect the cell, connect USB data directly to the controller, enter the documented UF2 bootloader and copy the calibrator image.
2. Check 3.3V, Q1 gate timing and amplifier output before calibration. Connect the USB CDC shell using a terminal at conventional 115200 8N1. CDC line coding does not control EC scan speed.
3. Type `ec` and Tab to confirm the matrix device name; this configuration uses `kscan0`.
4. With all 60 mechanisms installed, run `ec kscan0 calibration start`. Leave keys released during low-value sampling, then slowly press each key as prompted, releasing after its asterisk, until complete.
5. Run `ec kscan0 calibration export` and retain the output, then explicitly run `ec kscan0 calibration save`.
6. Power cycle, confirm restoration and use `ec kscan0 calibration load` if needed. Flash the normal image and check every key again. Avoid erasing settings while updating firmware.

A few installed sensing cells are useful for waveform/noise checks; complete calibration requires every valid position. Keep supply stable. Recalibrate after changes to sensing geometry, analog gain or dome preload.

Fn+1/2/3 selects BLE profiles, Fn+4 clears the current profile, Fn+H/J/K/L are arrows, and Fn+Esc enters the bootloader. See `yakb.keymap`.

ADC uses D19/P0.02/AIN0, not D18. The active-low power GPIO gates only the amplifier. Mux and controller VCC remain enabled while polling. Initial waits are 4/8/12 ms; measure actual frames, first-tap reliability and current. Deep sleep is disabled because no independent reliable wake circuit is present. Compilation does not validate analog range, RF, runtime or temperature.

## Reviewed fixes and dual transport

Before building, run `scripts/prepare_firmware.py` to apply the [hash-checked driver patch](patches/README.md). It fixes first taps after idle, invalid calibration endpoints and division by zero during constant-ADC calibration. The cooperative priority parameter is 15 (actual -1); kernel assertions are enabled. 960 first-tap logic scenarios and the actual constant-ADC calibration routine pass; these are not hardware latency measurements.

USB HID and BLE HID are both enabled. Fn+5 selects USB; Fn+6 selects BLE. Fn+1/2/3 selects BLE profiles. USB is initially preferred, and manual output selection persists. One selected endpoint receives reports at a time. A data cable supports wired use without a connected battery. Select BLE to type wirelessly while USB supplies power; the battery switch must be on for charging.
