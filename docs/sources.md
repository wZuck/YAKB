# Sources, provenance and licenses / 来源与许可

Date / 日期: 2026-10-22. Revisions below identify the inspected source snapshots; they are not warranties of physical compatibility.

| Source | Inspected revision | Use in YAKB | License boundary |
| --- | --- | --- | --- |
| [PH60](https://github.com/ph-design/PH60) | `e8900d68731d771cdebe9a7af88a47c0df994402` | Printed HHKB 6u case, battery and assembly reference; no case mesh copied | Upstream CC BY-NC-SA 4.0. Reusing its actual CAD requires following that license; YAKB's original case is separately generated |
| [Lot60](https://github.com/Lotlab/Lot60-BLE-Keyboard) | `ffb3c3220dcff5eae9413eb787d11f40b23d286f` | Measured outline/mount interface reference; no nRF52810/CH554 circuit copied | Upstream CC BY-SA; preserve upstream terms for actual copied derivatives |
| [HSKB](https://codeberg.org/Dev01-D/HSKB) | `51c04365e04c22e0ea9d1283d1f46b1ee6a6fcb6` | HHKB 6u layout comparison; last number-row x=15 corrected to x=14u | README identifies MIT; no mesh or firmware source copied |
| [Tako](https://github.com/ssbb/tako) | `5aa952ab5d5dc0c83aef36756252b27efc64e4cd` | Copied EC electrode, nice!nano and NiZ plate-cut footprints; layout is newly generated | MIT, copyright 2023 ssbb; full notice in [tako-MIT.txt](../licenses/tako-MIT.txt) |
| [EC60](https://github.com/4pplet/EC60) | `b9c04625bb9944f6fb806aa571da8592cdff8565` | Analog sensing topology comparison | MIT, Cipulot 2022; reference only |
| [ZMK](https://github.com/zmkfirmware/zmk) | `4dd95d7840eb3d5a3f59bb29fbf1ab054715ef85` | Firmware platform; dependency, not vendored source | MIT and dependency licenses; frozen manifest supplied |
| [EC support module](https://github.com/petejohanson/ec-support-zmk-module) | `bcb61bdee0a548976bea8f376f8cdec6b4ffd5fe` | EC scanner and calibration support | Retains its upstream license; dependency, not vendored source |
| [agentpad13](https://github.com/yuz207/agentpad13) | User's local soldering page | Visual organization reference for the offline workbench; original YAKB HTML/CSS/JS and generated images | No PCB image or assembly text copied |

## Primary part and firmware references

- [nice!nano documentation](https://nicekeyboards.com/docs/nice-nano/): power, charging, VCC and assembly. [Pinout and schematic](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/): D19 is P0.02/AIN0; D18 is not the ADC used here.
- [TI OPA350](https://www.ti.com/product/OPA350): operating supply and typical quiescent current. SOIC-8 `OPA350UA` pin map is explicit in the schematic.
- [TI SN74HC4051](https://www.ti.com/product/SN74HC4051): channel addressing, inhibit and analog supply limits; select SOIC-16 `SN74HC4051D`.
- [Alpha & Omega AO3401A](https://www.aosmd.com/products/mosfets/low-voltage-mosfets-12v-30v/ao3401a): SOT-23 P-channel gate/source/drain identity.
- [NiZ](https://www.nizkeyboard.com/): official EC mechanism/switch pack descriptions. Do not assume a housing/slider/ring pack includes domes or sensing conical springs. Verify exact generation, contents and current availability before buying.
- [ZMK external modules](https://zmk.dev/docs/development/module-creation) and the pinned EC module source describe build integration. This project records actual builds rather than assuming upstream native EC support.
- [FreeRouting](https://github.com/freerouting/freerouting/releases/tag/v2.5.0): routing tool v2.5.0. Interchange proxy geometry is not manufacturing geometry; the complete native board is authoritative.

## Design ownership and interpretation

Original YAKB generator code, design data, case/plate geometry, documentation and workbench are released under the root [MIT license](../LICENSE). KiCad footprint material retains its [library license and attribution](../licenses/KiCad-library-notice.md). The copied Tako footprints retain their separate MIT notice. Manufacturer trademarks identify compatible parts only. Third-party case geometry is not bundled, and no upstream source is relicensed by this repository.

中文：PH60 与 Lot60 仅作为方案和尺寸接口参考；如果以后直接复用其 CAD、PCB 或网格，必须另行遵守对应原始许可，不能因本项目根目录是 MIT 就改写上游许可。当前实际复制的 Tako 封装已保留完整许可。此表中的版本号也不等于实物兼容认证。

Additional case references: [Bakeneko 60 V3](https://github.com/kkatano/bakeneko-60) (MIT, proportions and low front), [ECneko60](https://github.com/mattyintegrals/ecneko60) (first-person NiZ adaptation log), and the [HSKB community fork](https://github.com/hungrygeek/HSKB). No meshes copied. See the [case design record](case-design.md).
