# YAKB A0 soldering and assembly order


[Open the offline soldering workbench](../hardware/soldering/index.html): 18 illustrated steps, searchable references, saved progress, zoom and print.

[简体中文](soldering-guide.zh-CN.md) · [Schematic](../hardware/YAKB.kicad_sch) · [BOM](../hardware/BOM.csv)

This is the first-article procedure for an engineering prototype. No physical soldered unit has yet been validated. Start with the fit coupon and current electrical reports. Pictures indicate locations; net names and pin numbers determine electrical connections.

![Layout, underside electronics and height budget](../assets/design-overview.png)

## 1. Prepare and identify the faces

Use a temperature-controlled iron, flux, fine solder, tweezers, magnification, braid, multimeter and current-limited USB data source. EC debugging also needs an oscilloscope; a current profiler is useful for battery measurements. Set soldering temperature from the solder/component requirements and avoid prolonged heating.

Electrodes are on F.Cu; most electronics are on B.Cu. View the underside directly rather than mirroring a back-view image again. In PCB front coordinates, U1 is in the bottom-right blank area with USB pointing left; in the already mirrored underside images, U1 is on the left and USB points right. A complete internal USB data extension takes that port to the case opening.

Keep the battery, domes, housings and keycaps away from soldering and cleaning. NiZ springs are **not soldered to the electrodes**. Do not tin the sensing copper or remove its solder mask.

## 2. Fit-check before buying the complete mechanism

Use the 13.9/14.0/14.1 mm coupon to establish housing orientation, latch fit and return motion. Repeat in the final plate material/thickness; an FDM coupon cannot certify a steel or FR4 plate. Check the stabilizer latch opening and the centered-stem 6u cap with 95.25 mm stabilizer spacing. The two 2.25u keys use 23.8125 mm spacing. Fix geometry before ordering complete plates.

## 3. Inspect the bare PCB

Check revision, dimensions, mask, mounting slots, damage and debris. Check VCC–GND, BAT_RAW–GND, BAT_SW–GND and AFE_3V3–GND for shorts. Verify all IC pin-1 marks, Q1 pinout, controller USB orientation and battery polarity. Keep U1, USB and the cell disconnected.

## 4. Solder the low 0805 parts first

Tack one pad, place the part, align it, then solder the other pad. Finish and inspect one value group at a time.

| Order | References | Value |
| --- | --- | --- |
| 4A | R1–R5 | 100Ω row series |
| 4B | R10–R24 | 100kΩ column bleed |
| 4C | R30 | 100kΩ feedback |
| 4D | R31, R32, R36 | 1kΩ gain leg, drain limit, gate series |
| 4E | R33, R34, R35 | 100kΩ inhibit/gate pull-ups |
| 4F | C1, C2, C3 | 100nF decoupling |
| 4G | C4 | 220pF C0G/NP0, not 220nF |
| 4H | C5 | 1µF local supply |

0805 means imperial 0805 / metric 2012. These resistors and ceramic capacitors are nonpolarized. In-circuit resistance includes parallel paths; lift one end if identification remains uncertain. Inspect for tombstones and bridges.

## 5. Solder the ICs and MOSFET

Fit U2/U3 CD74HC4051M96, U4 OPA350UA, then Q1 AO3401A. Tack diagonal pins, verify orientation and flatness, then finish all pins with flux and magnification.

- U2/U3: 16=VCC, 8=GND, 7=VEE tied to GND, 6=INH, 3=COM.
- U4: 7=AFE supply, 4=GND, 3=SENSE/IN+, 2=FB/IN−, 6=ADC output; 1/5/8 remain NC.
- Q1: 1=G, 2=S/VCC, 3=D/AFE_3V3. Verify the purchased manufacturer's drawing.

Inspect adjacent leads and check suspected bridges against the actual netlist. Some adjacent pins intentionally share GND.

## 6. Add through-hole connections and sockets

J1 is the horizontal JST S2B-PH-K, 2.0 mm pitch, pin 1 positive BAT_RAW and pin 2 GND. Plug polarity varies between battery vendors.

SW1 is a two-hole 2.54 mm **harness** connection for a SPST switch, not a manufacturer-specific slide-switch footprint. Connect BAT_RAW to BAT_SW through the switch; retain the switch near the bottom service window with strain relief. SW2 connects a normally-open reset button between RESET and GND.

Align two low-profile 12-pin sockets with an unpowered module or jig. Tack corners, finish, remove the module and inspect. Trim leads. The amplifier ADC escape uses a 0.25 mm drilled via near a lead pad; inspect for solder wicking and reflow the fillet if needed. The complete module/socket protrusion must stay within the 6.5 mm envelope. RF, clocks, charging and the module's USB-C connector need no user soldering. Leave BOOST open. Do not connect the battery yet.

## 7. Clean, dry and recheck without power

Follow flux cleaning requirements, especially around SENSE, C4, the amplifier and mux inputs. Dry completely. Recheck values, orientations, shorts, and switch continuity/isolation. A capacitor can cause a momentary resistance change; a persistent near-zero reading needs investigation.

## 8. First power is USB only

Fit U1 and use a current-limited USB data source, starting around a 100 mA limit. Disconnect if it limits unexpectedly, heats or shows bad voltages. First connect directly to the module, then validate the internal extension separately.

These are **existing component pads**, not separately numbered test-point footprints:

| Net | Probe location | Expected behavior |
| --- | --- | --- |
| GND | U1-23 / J1-2 | Voltage reference |
| VCC | U1-21 / U2-16 / U3-16 | Nominal 3.3V when module external power is on |
| AFE_GATE | Q1-1 | High=off; low=on |
| AFE_3V3 | U4-7 / Q1-3 | Powered during scans/calibration |
| Mux inhibits | U2-6 / U3-6 | High disables; never both low |
| SENSE | C4-1 / U4-3 | Small charge/discharge signal |
| ADC | U4-6 / U1-18 (D19) | Target 0–3.3V, no persistent saturation |
| DRAIN | R32-1 | Low for discharge, high impedance for sampling |

An unpowered AFE can legitimately read 0V when scanning is off. A multimeter averages pulsed rails; use a scope for timing. A probe adds capacitance to SENSE, so use an appropriate low-capacitance probe and record its loading.

## 9. Firmware and a small key group

Flash the configuration matching this pin map. Double-tap reset for UF2 bootloader entry. Begin with a small set such as Esc/1/2/3 at the correct plate height; the test mask must match the installed positions. Use the `enable_ec_calibrator` snippet and shell completion under `ec` to select the actual device and `calibration start/save/load/export` commands. Record baseline, full-press range, noise and hysteresis; verify cold-start restoration. Then install/calibrate all 60 keys. Test fast taps, slow presses, sustained holds, chords and power transitions before lowering thresholds.

## 10. Connect the cell only after USB checks

Disconnect USB and turn the physical switch off. Measure the **complete** cell envelope including protection PCB, wrapping and lead exit; maximum is 60 × 35 × 5.5 mm. Confirm positive voltage at the contact mating with J1-1 relative to J1-2. Cell protection does not provide board-level reverse-polarity protection.

Connect the cell, switch on, measure rail/current and check BLE. Then validate USB charging and temperature. Default charge current is approximately 100 mA; keep BOOST open. With the battery switch off, the cell cannot charge. Insulate the bay and keep leads, sharp solder ends and screw tips away from the pouch; retain it without compression.

## 11. Assemble the mechanism last

Disconnect both supplies again. Clip housings into the validated plate, align domes and clean conical sensing springs with their electrode centers, and fit the proven stabilizers/6u cap. Close the assembly gently at its designed height; do not bend the PCB or squeeze the domes to compensate for bad dimensions. Treat central tray posts as supports until housing/head clearance has been checked.

Check BLE with and without the bezel, route the USB extension without side-loading the module socket, retain the cell and perform complete calibration. Record coupon size, stabilizer/cap specification, stack height, cable, cell, calibration, temperature, working-state currents, first-tap response, USB/BLE switching and release events. Only observed results may be marked passed.

## Hidden case fasteners

Install eight M2 inserts (nominal OD 3.2 × L3 mm, test in the supplied 3.0 mm bores) from the underside of the bezel. Keep the top surface intact. Use M2 socket heads no larger than Ø3.8 × 2 mm: three M2×20 at the rear, two M2×18 at the sides, and three M2×16 at the front. Insert all screws from below. The model gives 3 mm engagement and at least 0.94 mm head recession; do not substitute longer screws. The plate edge notches clear the bezel bosses. PCB support insert holes remain a separate 3.3 mm system. Keep cables, foil and metal tape out of the antenna window.
