# YAKB A0 fabrication notes

[简体中文](README.zh-CN.md) · [Checks](../reports/design-checks.json)

The complete Gerber and separate PTH/NPTH files come from the checked native board. This is an unfabricated engineering prototype: build and measure a first article and fit coupons before larger production.

| Item | Specification |
| --- | --- |
| Outline | 285.0×94.6 mm, R2, open side slots, internal rectangular clearance and mounting slots |
| Copper order | **F.Cu → In1.Cu → In2.Cu → B.Cu**, four layers |
| Thickness | Nominal 1.6 mm FR4 |
| Planning stack | 0.035 mm each copper; 0.20/1.04/0.20 mm dielectrics; 0.01 mm each mask, total 1.6 mm |
| Stack constraint | Planning values; confirm a manufacturable standard 1.6 mm stack with the fab. No controlled impedance. Calibrate EC on the actual dielectric |
| Tracks / clearance | 0.20 mm normal, 0.15 mm minimum neck; 0.20 mm copper clearance |
| Copper-to-edge | 0.25 mm minimum |
| Through vias | Ø0.60/0.30 mm normal; local Ø0.45/0.25 mm escape; 0.10 mm minimum annulus |
| Mask | Keep sensing electrodes covered; no paste or added solder on them |
| Inner layers | No tracks/pours within 6 mm of sensing centers; no solid inner power/ground planes |
| RF | Preserve the all-layer antenna keepout |

Upload both inner Gerbers; this is not a two-layer order. Drill files are separated into plated/non-plated; oblong drills use routed slots. Preserve open side slots and the internal rectangle in Edge.Cuts. There are no blind/buried vias, backdrills or impedance requirements.

B.Paste is optional for a manual stencil; default assembly follows the hand-solder guide. Confirm the actual battery connector polarity. The PCB order does not include NiZ mechanism parts, caps, stabilizers, protected cell, controller, sockets, harnesses or case. Validate a final-material switch/stabilizer coupon before cutting a complete plate.
