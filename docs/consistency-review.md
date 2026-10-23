# Repository consistency audit

[简体中文](consistency-review.zh-CN.md) · [File/revision map](file-map.md) · [Machine record](../reports/repository-consistency.json)

Reviewed 2026-10-23. The current assembly is B1.1 with the shared A0 mainboard, plate and bezel. This review changes no copper, GPIO or enclosure geometry; it reconciles variant selection, instructions, calculations and delivered tables.

| Finding | Correction |
| --- | --- |
| Root README recommended B1.1 but centred A0 case dimensions, 40 positions and downloads | Both homepages now describe B1.1's maximum 299×136.6 mm envelope, 46 populated board/harness positions plus one FPC, matching base/lid and downloads |
| Several older pages lacked scope, mixing USB extension and direct access | Explicit A0 scope plus a file/revision map distinguishing shared, current and historical files |
| Design text claimed CAD retained PCB y, contradicting exports | Construction y points toward the typist; delivered CAD Y=-y; printable STL adds bed orientation |
| Front height mixed 21.0/21.4 mm, battery gap retained 0.75 mm | Main-body front/rear 21.4/25.1 mm and minimum cell/base clearance about 0.526 mm, matching parameters/reports |
| Total scan current counted background a second time | Weight scan and wait currents separately; refresh both electrical reports and runtime tables. A0 mixed-use estimate about 12.8 days/1000mAh; B1 continuous activity about 202–203 hours; neither measured |
| Mainboard U1 DNP counted as populated; FPC absent from B1 inventory | Explicit DNP and cable categories; consolidated electronics BOM agrees with 46 board/harness positions + 1 cable + 1 DNP + 60 electrodes = 108 records |
| Connector coordinates used pad centroids and generic footprint names | Use native saved-board origins, values and footprint names; distinguish JMAIN origin (0,0) from pin-group centre (20,9.5) |
| All base parts labelled through-hole; battery switch note allowed a momentary button | Correct SMT/through-hole labels, maintained SPST SW1 and normally open momentary reset SW2 |
| Shared B1 images retained A0 stage numbering and ambiguous viewing direction | Regenerate native-board images with 21-step numbering; distinguish mirrored mainboard backs from small-board top views; cable coordinates display “—” |
| Pack instruction applied one-pouch dimensions to the whole pack and excluded single-pouch 1S | Retain protected single 1S, check each multi-pack bay and shared PCM separately; multiple pouches require a factory protected single-output pack |
| Few-key bring-up implied full 60-key calibration | Observe waveforms first; prebuilt calibration needs all 60 mechanisms; subset calibration needs matching test firmware |
| Modular ERC checker omitted `sheets[].violations` | Correct both checkers and reject injected ERC-sheet, DRC, airwire and parity findings; saved and freshly rerun native reports remain clear |
| Per-pad CSVs retained pre-routing empty NC net names | Extract all four module-board tables from saved native boards and include them in output hashes |

Coverage: every Git-managed and newly delivered file is SHA256-catalogued; JSON/CSV/Python parse, ZIP CRC, PNG decoding, GLB/UF2/STL/STEP/PDF framing, XML/DXF parsing, local Markdown/HTML links, exact BOM/guide/native footprint origins, 24 FPC paths, fresh ERC/DRC for the mainboard and four module boards, existing solid checks and render/fabrication/firmware hashes. The machine record lists each file's actual checks; format integrity does not prove every engineering property.

Run KiCad Python `verify_modular.py` first to refresh extraction, then project Python `verify_release.py`, `verify_modular_release.py` and `verify_repository.py --native`. Refresh changed artifacts using the [reproduction notes](reproduce.md); do not merely rewrite hashes to hide stale files.

Physical qualification remains pending: NiZ/stabilizers, FPC mating/latching, actual USB height and insertion loads, scan/charging noise, RF, temperature and runtime. Browser policy blocked opening the local guide during this review, so no browser-interaction pass is claimed; delivered HTML/JS, links, data and generated images were checked.
