# KiCad library attribution

The native PCB embeds standard KiCad footprints. The standalone local
`hardware/YAKB.pretty/Battery_PH2.kicad_mod` is derived from KiCad's
`Connector_JST/JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal.kicad_mod` as installed
with KiCad 10.0.7. The project copy uses the horizontal connector body/courtyard and model, retains the YAKB through-hole pad sizes, and is normalized for bottom-side assembly. Through-hole soldermask openings are explicitly preserved.

37 placed standard library models are included in the exported populated STEP/GLB geometry; the native PCB retains their KiCad model references. These models retain the KiCad library terms too.

Source: https://gitlab.com/kicad/libraries/kicad-footprints

Copyright: KiCad library contributors. The footprint/library material retains
CC BY-SA 4.0 with the KiCad electronic-design exception; see the accompanying
[original license](KiCad-LICENSE.md). Original YAKB MIT files do not relicense
this library material.

The EC/nice!nano/plate-cut footprints originate from Tako under its separate
MIT notice. The local EC copy moves assembly-only graphics to Dwgs.User, and
the controller copy removes inaccurate upstream Pro Micro model dependencies.
Their copper and sensing geometry is preserved; the controller through-hole mask openings have been corrected. See [Tako notice](tako-MIT.txt).
