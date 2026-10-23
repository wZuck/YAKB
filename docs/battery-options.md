# Multi-pouch battery fit study

> **Scope: A0 baseline / historical record.** The current assembly is B1.1; use the [B1.1 notes](modular/README.md) and [file/revision map](file-map.md) for the separate controller, direct USB, dedicated base and FPC. Do not populate the mainboard U1 MCU.

[简体中文](battery-options.zh-CN.md) · [CAD results](../reports/battery-study.json) · [Power model](electrical-analysis.md)

The present case accommodates **three 60×35×5.5 mm pouch envelopes** in construction coordinates (negate Y for delivered CAD) at `(62,23,-7.8)`, `(144,23,-7.8)` and `(226,23,-7.8)`, tilted with the floor. All clear the actual base, PCB, 37 component models, module, USB and hidden screws. Each has about 0.526 mm minimum base clearance and 2.856 mm PCB clearance. Insulation/retention must fit inside the remaining gap without compression.

B1.1 uses its [dedicated three-bay base](../mechanical/modular/case_base_B1_three_bay.stl) and [pod lid](../mechanical/modular/pod_lid_B1.stl), sharing the A0 bezel and plate. The 12.8/25.5/38.3-day figures below are A0 mixed-use scenarios, not B1.1 measurements. The [modular analysis](modular/README.md) separately estimates continuous activity with FPC/ADC capacitive loads.

![Optional three-bay base and pack envelopes](../assets/battery-study-render.png)

An optional [three-bay STEP](../mechanical/case_base_three_bay.step) / [STL](../mechanical/case_base_three_bay.stl) reuses the PCB, bezel, plate and fasteners. The single-bay base remains available. Two extra fences accept a two-pouch pack with one empty bay or a three-pouch pack. A shared protection board has a 25×12×3 mm envelope at x=49.5…74.5, y=46…58, z=-8.5…-5.5. Confirm actual protection/wire drawings.

| Pack | Target capacity, assuming 1000 mAh/pouch | Central mixed-use estimate | Ideal 100 mA charge lower bound |
| --- | --- | --- | --- |
| 1S single pouch | 1000 mAh | 12.8 days | 10 h |
| Factory 1S2P | 2000 mAh | 25.5 days | 20 h |
| Factory 1S3P | 3000 mAh | 38.3 days | 30 h |

Two pouches are a reasonable capacity/weight compromise; three use the designed bay count, not a proven maximum of every possible packing arrangement. The capacity is a target, not a qualified cell SKU. Measure complete seams, wrapping, lead exits and insulation; a size code alone is insufficient.

Use only a **factory-assembled protected 1S pack**, 3.7 V nominal / 4.2 V full, with matched cells, appropriate branch fault protection and one output to J1. Do not add DIY parallel battery sockets, combine unmatched packs or use 2S/3S. Parallel capacity adds without increasing voltage, but unequal cell voltages cause equalization current. [SparkFun battery connections](https://learn.sparkfun.com/tutorials/what-is-a-battery/usage)

Keep the default 100 mA charging setting; real charging exceeds the ideal bounds. Extra conductive pouch foil can change EC parasitics. Recalibrate with the final pack and repeat RF, false-trigger and charging-temperature tests. CAD clearance does not establish cell availability or physical validation.
