# File revisions and assembly selection

[简体中文](file-map.zh-CN.md) · [B1.1 assembly](modular/README.md)

The current assembly is **B1.1**, combining the unchanged A0 sensing mainboard, bezel and plate with B1-series modular hardware. `B1` in filenames identifies the series; the FPC / enclosure interface is revision B1.1. Rigid-board copper is unchanged and native titles retain B1. Renaming everything to one revision would hide this distinction.

| File group | Current use / rule |
| --- | --- |
| `design/yakb.json`, `scripts/circuit.py`, `hardware/YAKB.*` | Shared A0 board/mechanical baseline. Its schematic and base BOM retain U1; B1 installs only the interposer there |
| `hardware/BOM.csv` | A0 base BOM; not a standalone B1 purchasing/population list |
| `hardware/modular/BOM-B1-complete.csv` | Consolidated electronics: 46 populated board/harness positions, one FPC, one U1 DNP and 60 unsoldered electrodes; JMAIN quantity 1 means one assembly of 24 pins |
| `hardware/modular/BOM-B1.csv` | Module/case delta list, including connectors, fasteners, pod and coupons; not the complete mainboard BOM |
| `design/modular.json`, `design/fpc-interface.json` | B1.1 placement, USB and FPC interface contract; sample qualification pending |
| `hardware/modular/YAKB-controller-B1.*` / `YAKB-interposer-B1.*` | B1 rigid boards; the sole nice!nano is on the carrier; interposer JF1/R1 face the mainboard |
| `hardware/modular/YAKB-shaped-FPC-B1.*` | Full B1.1 custom FPC, not a generic straight FFC; 24 independent A:n→B:25−n conductors |
| `hardware/modular/YAKB-FPC-coupon-B1.*` | Bench coupon only, 25 mm tip separation; cannot replace the full installed cable |
| `hardware/modular/*-netlist.csv` | Per-pad tables from saved native PCBs, including actual NC names; not pre-routing intermediate data |
| `fabrication/YAKB-A0-gerbers.zip` | Shared four-layer mainboard fabrication set, 1.6 mm board |
| `fabrication/modular/*` | Separate sets for two 1 mm two-layer rigid boards and 0.20 mm single-copper-layer full/coupon flex; stiffened terminals 0.30±0.05 mm; not default two-layer FR4 |
| `mechanical/modular/assembly_B1.step` | Current assembly, with no MCU at mainboard U1 |
| `mechanical/modular/case_base_B1*.stl`, `pod_lid_B1.stl` | Current single/three-bay base and matching pod lid |
| `mechanical/case_bezel.*`, `plate_case.*`, `niz_fit_coupon.*` | Shared A0/B1 bezel, plate and NiZ coupon |
| `mechanical/modular/rear_pod_fit_coupon.*` | Actual crop of the current base, using the same lid; not a standalone product case |
| `mechanical/modular/*-native.step` | KiCad board/component exports; flex uses uniform 0.20 mm board thickness, without terminal stiffeners |
| `mechanical/modular/shaped_fpc_envelope.step`, `fpc_mating_coupon_envelope.step` | Full/coupon mechanical envelopes including 0.30 mm stiffened terminals |
| `mechanical/case_base*`, `assembly.step`, `module_envelope.step`, `usb_plug_envelope.step` | Historical A0 assembly: front-right underside controller and incomplete USB extension/retention; not B1 case files |
| `hardware/soldering/b1/`, `assets/modular/` | Current B1.1 workbench and geometry-based renders |
| `hardware/soldering/`, old root `assets/` assembly images | A0 historical guide / baseline drawings; B1 separately generates shared-board images with correct 21-step numbering |
| `firmware/prebuilt/yakb-a0*.uf2` | Shared A0/B1 firmware; same GPIO/matrix, retained build names; recalibrate after added filtering |
| `reports/modular*` | Current modular checks; root board/electrical/mechanical/battery reports describe the shared A0 baseline and must be read with the modular reports |

Coordinates: PCB, JSON, CSV and construction reports use x right, y toward the typist, z up. Delivered STEP/DXF use X right, Y rear, Z up, so Y=-y. Printable base/lid STL additionally rotates onto the build plane and is not an assembly-datum model. Mainboard back-view soldering images are already mirrored; small-board plans are native top views.

A0 plan envelope is 299×108.6 mm; B1.1's local rear-left pod increases the maximum to 299×136.6 mm. Main-body front/rear nominal shell heights are 21.4/25.1 mm, excluding caps/feet; the pod has a separate local envelope. Mixed-use battery-study days and B1 continuous-activity hours use different assumptions and are not directly comparable or measured runtimes.

The [physical qualification sheet](modular/qualification-checklist.csv) remains entirely pending. Native-file checks cannot mark physical measurements as passed.
