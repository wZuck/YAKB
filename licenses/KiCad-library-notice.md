# KiCad library attribution

The native PCB embeds standard KiCad footprints. The standalone local
`hardware/YAKB.pretty/Battery_PH2.kicad_mod` is derived from KiCad's
`Connector_JST/JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical.kicad_mod` as installed
with KiCad 10.0.7. The project copy retains the connector geometry and removes
external 3D model dependencies; it is normalized for the bottom-side assembly.

Source: https://gitlab.com/kicad/libraries/kicad-footprints

Copyright: KiCad library contributors. The footprint/library material retains
CC BY-SA 4.0 with the KiCad electronic-design exception; see the accompanying
[original license](KiCad-LICENSE.md). Original YAKB MIT files do not relicense
this library material.

The EC/nice!nano/plate-cut footprints originate from Tako under its separate
MIT notice. The local EC copy moves assembly-only graphics to Dwgs.User, and
the controller copy removes inaccurate upstream Pro Micro model dependencies.
Their pad and sensing geometry is preserved. See [Tako notice](tako-MIT.txt).
