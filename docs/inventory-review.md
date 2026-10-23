# Inventory review and purchasing

> **Scope: A0 baseline / historical record.** The current assembly is B1.1; use the [B1.1 notes](modular/README.md) and [file/revision map](file-map.md) for the separate controller, direct USB, dedicated base and FPC. Do not populate the mainboard U1 MCU.

[简体中文](inventory-review.zh-CN.md) · [BOM](../hardware/BOM.csv) · [Electrical analysis](electrical-analysis.md)

Reviewed on 2026-10-23 using the supplied workbook's inventory-detail sheet. Quantities are derived from purchase records, not a physical stocktake or qualification. Only relevant specifications and decisions are recorded here; the workbook and order data are not committed.

**Retain nice!nano v2 and stop the XIAO migration. Keep the current PCB, 0805 hand-solder footprints and mechanical design. Buying the small missing parts is preferable to redesigning around this inventory.** Correct the stale U2/U3 BOM ordering code to `CD74HC4051M96`, matching the existing schematic, PCB and circuit source; add a BOM consistency check.

## Candidate stock

| Inventory row | Part | Decision |
|---|---|---|
| 39 | One nRF52840 board sold under a nice!nano-compatible description | Candidate U1 only. Check every GPIO, BAT/3V3/RESET, USB direction, height, charger current and antenna placement. The listing does not prove original-v2 electrical or mechanical equivalence |
| 30 | Five PTS645SM43SMTR92LFS switches | Candidate wired SW2 reset. A 6×6 mm SMT switch does not fit the current 2.54 mm two-hole footprint directly; verify contacts, insulation and mounting with a harness or adapter |
| 26–28 | Four switches per actuator-height variant, listing mixes MSK-12C02/MSK12C01-07 | Candidate SW1 harness. Confirm exact part, contacts, current rating and fit before use; do not invent an SMT footprint from the listing |
| 41–42 | Two types of four-strand wire, 0.5 m each | Possible low-speed control wiring after gauge/insulation/strain-relief checks; not a USB data extension |
| 48,51,57 and related rows | 0402 capacitors/resistors including 100nF,1kΩ,1µF | Some values match; packages do not. Retain 0805 for hand soldering |
| 49 | 0805 10µF/25V X5R, 20 received and 40 in transit | Not the required 100nF/1µF/220pF values. Do not alter analog behavior or startup load merely to consume stock |
| 44–46 | 15pF/20pF and 0603 10Ω | Do not substitute for 220pF C0G or 100Ω row resistors |
| 37 | Two 301230 cells listed as 110mAh | Not the production battery choice: protection and charge rating are unspecified. A 100 mA charge setting needs qualification. Linear scaling of the unmeasured runtime model gives only about 1.4 days per cell; do not wire independent cells in parallel |
| 17,19 | 7U stabilizer kit and 133-key cap set | A 7U bar does not meet the centered 6u/95.25mm requirement; cap count does not prove 6u compatibility. Inspect individual 2u parts before reuse |
| 21–25 | Short screws and 6/18mm brass standoffs | Not substitutes for M2×16/18/20 bottom screws or heat-set inserts. An 18 mm standoff is not an 18 mm screw; the 4 mm head on the M2×5 stock exceeds the current 3.8 mm head envelope |
| Other listed electronics | TTP223, 1N4148,RGB,OLED | Do not add them. TTP223 does not replace this EC front end; per-key diodes are unnecessary for this topology; displays/lighting add power and soldering |

Check the reset switch's SPST-NO function and SMT form against [C&K specifications](https://www.ckswitches.com/products/switches/product-details/Tactile/PTS645/PTS645SM43SMTR92LFS). Use the [original nice!nano pinout/schematic](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/) as a qualification reference, not proof of clone behavior.

## Electronic purchases

These are per-board fitted quantities. Buy a few spares; unqualified stock candidates are not deducted.

| Part | References | Qty | Selection |
|---|---|---:|---|
| CD74HC4051M96 | U2/U3 | 2 | SOIC-16 HC, not HCT/CD4051B |
| OPA350UA | U4 | 1 | SOIC-8; no arbitrary amplifier substitution |
| AO3401A | Q1 | 1 | SOT-23 P-channel with matching pinout |
|100Ω | R1–R5 | 5 |0805, preferably 1% |
|100kΩ | R10–R24,R30,R33–R35 | 19 |0805, preferably 1% |
|1kΩ | R31/R32/R36 | 3 |0805, preferably 1% |
|100nF | C1/C2/C3 | 3 |0805 X7R, at least 10 V |
|220pF | C4 | 1 |0805 C0G/NP0 |
|1µF | C5 | 1 |0805 X5R/X7R, at least 10 V; check effective capacitance |
| JST S2B-PH-K | J1 | 1 | Horizontal 2P plus matching lead and verified polarity |

Also qualify U1 and low sockets, switch mounting, USB data extension, protected 1S pack, NiZ mechanisms, centered 6u cap/stabilizers, plate and case. Bottom screws are three M2×20 rear, two M2×18 side and three M2×16 front with eight M2 inserts. Follow the [assembly guide](soldering-guide.md) for head and insert dimensions.

## Additional firmware finding

The pinned ZMK `battery_nrf_vddh.c` uses SAADC logical channel 0. The old EC configuration also used channel 0, so whichever initialized later overwrote the earlier input/gain setup.

EC now uses **logical channel 1 with physical AIN0/P0.02 unchanged**; battery retains logical 0/VDDHDIV5. This does not move the PCB connection to AIN1. The regression uses the actual battery initializer in both initialization orders, and reproduces the collision with the old allocation. Both normal and calibration builds are refreshed; packaging checks actual DTS allocation. Hardware ADC contention, radio load and real noise remain first-article tests.
