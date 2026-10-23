# YAKB B1.1: separate controller carrier and shaped FPC

[中文](README.zh-CN.md) · [Pin table](../../hardware/modular/FPC-pinout.csv) · [B1 soldering workbench](../../hardware/soldering/b1/index.html) · [Module/case delta BOM](../../hardware/modular/BOM-B1.csv)

B1 moves the nice!nano from underneath the front-right of the sensor PCB to a separate rear-left carrier. USB-C plugs directly into the module through the **left side at the rear corner**, removing the internal USB extension. A passive interposer occupies the original U1 holes; **do not install another MCU on the mainboard**. Keep the A0 sensor PCB, HHKB bezel and plate, and use the B1 base and pod lid.

These are reviewable engineering prototype files. Connector mating dimensions, FPC stiffeners, module mounting height and USB plug fit still require qualification before making a complete keyboard. Gerbers support quotation and engineering samples; they are not a production approval.

![B1 saved CAD assembly](../../assets/modular/B1-closed.png)


Use the [consolidated electronics BOM](../../hardware/modular/BOM-B1-complete.csv) plus the [module/case delta BOM](../../hardware/modular/BOM-B1.csv). There are 46 populated board/harness positions plus one FPC, one mainboard-U1 DNP and 60 unsoldered electrodes. Quantities count assemblies; JMAIN is one group of 24 pins. Small-board CSV coordinates are native footprint origins, not pad centroids; JMAIN origin is (0,0), with pin-group centre (20,9.5). See the [file/revision map](../file-map.md).

## Parts and files

| Part | File / size | Assembly |
| --- | --- | --- |
| Sensor PCB | [A0 PCB](../../hardware/YAKB.kicad_pcb), 285 × 94.6 × 1.6 mm, four layers | Populate other parts normally; U1 takes the interposer |
| Controller carrier | [B1 PCB](../../hardware/modular/YAKB-controller-B1.kicad_pcb), 82 × 24 × 1 mm, two layers | nice!nano on top, USB left, antenna right; JF1, 1 nF and 100 nF |
| Mainboard interposer | [B1 PCB](../../hardware/modular/YAKB-interposer-B1.kicad_pcb), 40 × 19 × 1 mm, two layers | 24 straight pins into A0 U1; connector and 47 Ω face the mainboard; 2.6 mm surface gap |
| Custom flex | [FPC PCB](../../hardware/modular/YAKB-shaped-FPC-B1.kicad_pcb) | 24 independent conductors, 1 mm terminal pitch; 25 mm tabs, body X-direction sections up to 26 mm; 26.1 mm across the locating ears; not generic straight FFC |
| Base | [Single-bay STL](../../mechanical/modular/case_base_B1.stl), [three-bay STL](../../mechanical/modular/case_base_B1_three_bay.stl) | Overall bounding rectangle 299 × 136.6 mm; only the left rear extends 28 mm; front height unchanged |
| Pod lid | [STL](../../mechanical/modular/pod_lid_B1.stl) | Two bottom-up M2×16 screws in blind inserts; four internal M2×4 carrier screws; no exposed top screws |
| Assembly | [STEP](../../mechanical/modular/assembly_B1.step) | Delivered X right, Y rear, Z up; mainboard top z=0 |

Both rigid boards, the installed flex and the short FPC coupon include native schematics, PDF, KiCad project and separate fabrication ZIP in [hardware/modular](../../hardware/modular/) and [fabrication/modular](../../fabrication/modular/). Mainboard/plate fabrication remains A0. The rear pod requires the custom B1 enclosure; this assembly is not a drop-in fit for arbitrary GH60 cases.

![B1 open view](../../assets/modular/B1-open.png)

The main PCB is raised 25 mm and the lid 60 mm for inspection in this image. These are not installed heights. Module, USB plug, battery and keycaps are clearance envelopes. Small-board connector/passive solids come from native KiCad models. Source hashes are in the [render manifest](../../assets/modular/render-manifest.json).

Plastic supports under the USB end, a front edge lip and a lid stop limit vertical motion with 0.30 mm nominal play, avoiding a roughly 48 mm unsupported FR4 cantilever. Insert the left-front board edge under the lip, lower the carrier, fasten it and close the lid. Qualify the printed clip and actual plug forces.

Printable STLs are oriented separately: base slope on the bed, pod lid outer face down with stops facing up. Assembly STEP retains the installed frame.

The accepted plug shroud envelope is **12 × 8 mm**, with a **14 × 10 mm** opening cut through both base and lid; remaining lid roof is 1.85 mm. Port centre and recess remain assembly datums for measurement. First print the [96 × 34.4 mm rear-pod fit coupon](../../mechanical/modular/rear_pod_fit_coupon.stl) and use the existing lid, real carrier/module and cable. It is cropped from the actual base and has an open front; it does not replace the complete enclosure.

## Contacts and power

Each connector is **Molex 200528-0240: 24 contacts, 1 mm pitch, bottom contact, 1.9 mm mated height**. The manufacturer lists 1 A/contact and 20 mating cycles, with limited online product information. That contact rating does not establish a 1 A rating for this flex. [Molex specifications](https://www.molex.com/en-us/products/part-detail/2005280240)

Carrier JF1 is A; interposer JF1 is B, rotated 180°. The custom flex maps **A1→B24, A2→B23 … A24→B1**, with exposed contacts on the same physical face. Verify contact face, pin 1 and every connection on samples. Commodity “same-side/opposite-side FFC” labels do not establish equivalence. The interposer net assignment is reversed to match the opposed connectors.

Carrier functions in order: `GND, VCC, GND, ROW0…ROW4, GND, MUX_A, MUX_B, MUX_C, MUX0_INH, MUX1_INH, DRAIN, AFE_ON_N, GND, ADC_FLEX, GND, RESET, GND, BAT_SW, BAT_SW, GND`. Use the CSV and native PCB as the authoritative pin numbering.

- Battery stays at mainboard J1 through SW1. Two BAT_SW conductors and seven GND conductors join the mainboard to the module; charging returns over the same path. Module VCC supplies the analog frontend.
- USB D+/D−, CC and VBUS remain within the assembled nice!nano and do not cross the flex. USB HID and BLE HID remain enabled; Fn+5/Fn+6 select the output. The firmware GPIO map is unchanged.
- High-impedance SENSE, FB and raw electrodes stay on the mainboard. Only the buffered ADC output crosses the flex: 47 Ω at the interposer, 1 nF C0G to GND at the carrier; 100 nF decouples VCC. Assembly uses 0805, SOIC and through-hole parts, plus two 1 mm-pitch connectors needing flux and magnified inspection. No bare QFN or RF matching network assembly is introduced.


Use the existing `firmware/prebuilt/yakb-a0.uf2` and `yakb-a0-calibrator.uf2`; their names retain the original shield identifier. B1 leaves GPIO unchanged, but collect fresh baselines and recalibrate after adding the ADC filter.

## Flex fabrication and outstanding fit checks

Quote **single-sided B.Cu, 35 µm copper, nominal finished flex thickness 0.20 mm**. KiCad retains two logical copper layers; F.Cu is empty and is not exported in the flex fabrication ZIP. Use flexible coverlay outside the contact windows: B.Mask uses one continuous region at each end for the exposed contacts, not ordinary FR4 soldermask. Trace width is 0.15 mm, clearance rule 0.10 mm and copper-to-edge rule 0.20 mm. Fingers are now 0.7 × 3.5 mm and reach the insertion edge. The 25 mm terminal has locating ears and a continuous coverlay opening. Non-contact-side stiffeners extend at least 5 mm; finished terminal thickness is 0.30 ± 0.05 mm. Gold must be at least 0.1 µm over 1–5 µm nickel; an unspecified default finish is insufficient. These nominal dimensions follow the manufacturer drawing with the exact part table verified, and still require physical mating qualification. See the [interface correction and coupons](interface-review.md).

Do not order this flex with a default rigid FR4 stack. The manufacturer drawing including 2005280240 now defines the nominal terminal geometry and 4 mm insertion depth. Un-dimensioned slot elevation, manufactured tolerances, retention and contact still require samples. Qualify the new [25 mm short coupon](../../hardware/modular/YAKB-FPC-coupon-B1.kicad_pcb) before making the installed flex. This is a static-installation flex with its curved plan outline manufactured directly; it does not require folding straight FFC into a curve. Provide slight vertical compliance during assembly and do not use the thin cable as a structural tie.

The interposer surface gap is 2.6 mm. Solder straight pins with an insulating height fixture, trim and inspect bottom clearance. Removing the mainboard is necessary to operate the interposer latch; never hot-plug. The nice!nano and USB socket are conservative envelopes. Qualify the purchased module's pin installation, actual port centre and plug shell first; adjust pod opening/carrier height and rerun clearance checks if necessary.

## Interference and power

The module antenna sits outside the mainboard and metal-plate projection. Its carrier all-copper keepout is local `x=26.27…43.27, y=6.5…18.5 mm`, clear of screws and the flex. A plastic lid does not certify RF performance: USB metal, inserts, hands and batteries still affect matching and retries. Compare bare/closed, USB/battery and single/three-bay assemblies for RSSI, disconnects and lost/stuck keys.

About 0.23 m of flex places digital controls beside the buffered analog output. Adjacent GND improves return paths but provides neither continuous shielding nor controlled impedance. GND flanks ADC. The ideal 47 Ω/1 nF time constant is about 48 ns, or 0.43 µs to half an LSB for a full-scale 12-bit step; this omits the amplifier, distributed capacitance and wireless preemption. Retain the present 5 µs pre-sample delay and 10 µs acquisition provisionally. Measure first frames, near/far keys, adjacent chords, charging and BLE traffic before changing timing. The original long SENSE routing risk remains; see [A0 analysis](../electrical-analysis.md).

With copper resistivity 0.01724 Ω·mm²/m, length 0.23 m and section 0.15×0.035 mm², each conductor is about 0.76 Ω. Ideal equal current sharing gives about 0.49 Ω through two BAT_SW and seven GND conductors: approximately 49 mV/4.9 mW at 100 mA, plus connectors, pins and rigid traces. Actual return currents need not share equally. Even ideal sharing through seven ground conductors gives about 11 mV between board grounds at 100 mA charging, potentially shifting ADC baselines. Compare unloaded/pressed distributions during charging, USB-only and battery-only operation; continuity alone is insufficient. Positive-wire drop also affects the cell-side CV tail and battery readings, so measure at the cell. Keep charging at approximately **100 mA, BOOST open**; a contact's 1 A rating does not authorize a higher charge current.

The new passives add no substantial DC load. Flex capacitance and RF retries add dynamic consumption. Assuming twelve digital conductors, 10–100 pF each, 5 kHz effective charging frequency and 3.3 V gives roughly 2–20 µA extra average current; this is not a measured upper bound. A conservative assumption of sixty full 3.3 V charge/discharge cycles per 7 ms frame adds about 28 µA for the 1 nF ADC filter; actual swings are usually smaller, and this is not a measured bound. Adding these terms to the A0 activity midpoint of 3.92 mA gives about 202–203 continuous hours from 1000 mAh at 80% usable capacity. B1 has no measured runtime improvement. Optional multi-cell packs must remain factory-built protected 1S2P/1S3P assemblies; do not parallel loose cells.

[Native reports](../../reports/modular/) verify connections, all 24 cable paths, original U1 hole alignment and layout. [Mechanical checks](../../reports/modular-mechanical.json) cover the selected solids. Passive physical-pin schematic symbols check connectivity, not nice!nano's internal circuitry. No impedance/EMC simulation or physical NiZ, charging, RF, mating or print-tolerance qualification has been completed.


The [B1 electrical calculation](../../reports/modular-electrical.json) uses saved native FPC trace lengths and records the exact assumptions. Recalculate with KiCad Python `scripts/analyze_modular.py`.

## Reproduction

1. Run `scripts/generate_modular_pcbs.py` with KiCad Python; route its two DSNs using FreeRouting to matching SES files, respecting hole and RF keepouts.
2. Run `scripts/finish_modular_pcbs.py`, then `scripts/generate_modular_flex.py` (also generates the short coupon) with KiCad Python. Route import reads `.render-cache/*-unrouted.kicad_pcb`, avoiding duplicate tracks.
3. Run `.venv/bin/python scripts/export_modular.py` for native checks/manufacturing/GLB/STEP, then KiCad Python `scripts/verify_modular.py` for pad-chain verification and native drawing extraction.
4. Run project Python `generate_modular_mechanical.py`, `verify_interface_samples.py`, `render_modular.py`, `generate_soldering.py` and `generate_modular_guide.py` in order. Run KiCad Python `analyze_modular.py` after refreshing the baseline power analysis. Final project-Python checks: `verify_release.py`, `verify_modular_release.py` and `verify_repository.py --native`. The Blender path is in the renderer; see [runtime instructions](../reproduce.md).
