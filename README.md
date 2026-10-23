# YAKB — Yet Another KeyBoard

[简体中文](README.zh-CN.md) · [B1.1 soldering workbench](hardware/soldering/b1/index.html) · [Assembly notes](docs/modular/README.md) · [File/revision map](docs/file-map.md)

The current assembly is the **B1.1 engineering prototype**: NiZ electrocapacitive mechanisms, a fixed 60-key HHKB layout, centered-stem 6u spacebar, nice!nano v2 / nRF52840 and ZMK, USB / BLE and a protected 1S battery.

The controller sits on a rear-left carrier, with USB-C directly accessible from the left side. Mainboard U1 takes only a passive interposer: **do not install a second controller there**. PCB, plate, case, fabrication files and geometry-based renders are supplied. Physical assembly, noise, RF, temperature and runtime remain untested. Qualify NiZ/stabilizer coupons, the short FPC and the rear-pod coupon before a complete build.

![B1.1 saved CAD assembly; keycaps and module are clearance envelopes](assets/modular/B1-closed.png)

| Item | Current B1.1 definition |
| --- | --- |
| Layout | 60 keys, HHKB Control position, split right Shift + Fn; left blocker 1.5u, right 2.5u; centered 6u space with 95.25 mm stabilizer spacing |
| Mechanism / plate | NiZ housing, MX-cross slider, silencing ring, separate dome and sensing conical spring; 1.6 mm plate with initial 14.0 mm R0.5 cutouts; qualify in final material |
| Sensing mainboard | Shared A0 four-layer board, 285 × 94.6 × 1.6 mm; no MCU at U1 |
| Daughterboards / FPC | 82 × 24 × 1 mm carrier, 40 × 19 × 1 mm interposer; 24-conductor custom shaped FPC and Molex 200528-0240 connectors |
| Hand assembly | Mainly SOIC, 0805 and through holes; the 1 mm-pitch FPC connectors need flux and magnification; no bare MCU, crystal or RF network assembly |
| Power | Protected 1S, approximately 100 mA default charging, BOOST open; multiple pouches require a factory 1S2P / 1S3P pack with one protection board |
| USB / BLE | Direct to the carrier's nice!nano; Fn+5 selects USB, Fn+6 selects BLE; one reporting endpoint at a time |
| Case | Dedicated B1 base and pod lid with shared A0 HHKB bezel and plate; maximum plan envelope 299 × 136.6 mm, with 28 mm extra depth only at the rear-left pod; no visible top screws |
| Case compatibility | Mainboard mounts reference GH60 / Lot60; the B1 pod is not a universal drop-in fit for commercial GH60 / Poker cases |

B1.1 has **46 populated board/harness positions + one FPC**, plus one mainboard-U1 DNP record and 60 unsoldered sensing cells. No per-key diodes, hot-swap sockets, RGB, display or separate USB controller are used.

File entry points:

- [Complete electronics BOM](hardware/modular/BOM-B1-complete.csv), [module/case delta BOM](hardware/modular/BOM-B1.csv), [FPC pin map](hardware/modular/FPC-pinout.csv). The electronics BOM excludes batteries, mechanisms and case hardware; use the assembly notes and delta BOM for those.
- [Mainboard PCB](hardware/YAKB.kicad_pcb), [mainboard schematic](hardware/YAKB.kicad_sch), [controller PCB](hardware/modular/YAKB-controller-B1.kicad_pcb), [interposer PCB](hardware/modular/YAKB-interposer-B1.kicad_pcb), [custom FPC](hardware/modular/YAKB-shaped-FPC-B1.kicad_pcb). The shared mainboard source retains the A0 controller symbol; the consolidated BOM controls B1 population.
- [B1 assembly STEP](mechanical/modular/assembly_B1.step), [single-bay base STL](mechanical/modular/case_base_B1.stl), [three-bay base STL](mechanical/modular/case_base_B1_three_bay.stl), [pod lid](mechanical/modular/pod_lid_B1.stl), [shared bezel](mechanical/case_bezel.stl).
- [Own-case plate DXF](mechanical/plate_case.dxf), [NiZ coupon](mechanical/niz_fit_coupon.stl), [short-FPC ZIP](fabrication/modular/YAKB-FPC-coupon-B1.zip), [rear-pod print coupon](mechanical/modular/rear_pod_fit_coupon.stl). DXF units are mm; do not cut `REFERENCE`.
- [Interface corrections and qualification](docs/modular/interface-review.md), [firmware/flashing](firmware/README.md), [reproduction](docs/reproduce.md), [sources/licenses](docs/sources.md).

Scripts check native electrical reports, selected solid clearances, fabrication ZIPs and render hashes. See [reports](reports/) and the [consistency audit](docs/consistency-review.md) for coverage and pending physical tests. File checks do not certify hardware operation.

A0 is the baseline for the shared mainboard, bezel and plate. Its [historical workbench](hardware/soldering/index.html), [case record](docs/case-design.md), [base electrical analysis](docs/electrical-analysis.md) and [battery study](docs/battery-options.md) are explicitly scoped. The A0 base and incomplete USB extension arrangement are not used by the current B1 assembly.

Original YAKB files use MIT; reused Tako / KiCad library material retains its own licenses. See the source record for attribution boundaries.
