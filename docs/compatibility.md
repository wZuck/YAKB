# YAKB A0 compatibility

> **B1.1 update:** This document describes the A0 baseline. Use the [B1 notes](modular/README.md) for the separate controller, direct USB, new base, FPC and assembly differences. Do not populate the A0 U1 MCU in B1.

[简体中文](compatibility.zh-CN.md). The default interface is the GH60/Poker tray family using measured Lot60 hole/slot coordinates. No commercial case model has been physically tested.

| Part | Status / requirement |
| --- | --- |
| YAKB base + bezel + plate_case | Generated from shared parameters; selected envelope checks pass; real NiZ, dome preload, stabilizers and cables remain first-article checks |
| GH60/Poker tray cases | 285×94.6 mm PCB target, conditional on posts, screw heads, underside parts, cell space, USB and plate retention |
| Metal 60% cases | Exact generation unverified; need a non-metal antenna window and adequate internal clearance |
| PH60 HHKB 6u printed case | Adaptation candidate; upstream plate is about 284.75×107.25×5 mm, unlike this 1.6 mm NiZ plate |
| Existing MX plates | Require a new HHKB/NiZ plate |
| Original HHKB/Topre caps | Not specified for the selected NiZ MX-cross sliders |
| Spacebar | Centered MX-cross 6u, 95.25 mm stabilizer spacing; 6.25u and offset-stem 6u do not fit |
| Dome sheet | Must match every key position; prefer individual domes or a deliberately adapted sheet |

PCB rear-left corner is (0,0), x right, y toward the typist, PCB top z=0. Units mm.

| Mount | X | Y | Width×height |
| --- | ---: | ---: | --- |
| Left open slot | 1.4579 | 56.5010 | 7.00024×2.49936 |
| Upper-left round hole | 25.1983 | 27.9006 | Ø2.4994 |
| Center slot | 128.1990 | 46.9998 | 5.00126×2.49936 |
| Lower-left rectangular clearance | 93.0991 | 82.5500 | 7.6×15.1 |
| Lower-center slot | 190.4984 | 85.2005 | 5.00126×2.49936 |
| Right open slot | 283.5402 | 56.5010 | 7.00024×2.49936 |

A slot does not prove that the housing, dome, washer or screw head fits. Import the actual case and `pcb_envelope.step`, check all posts, then add actual switch and cable geometry. Start with a 1:1 printout and NiZ/stabilizer coupons. Do not bend the PCB to compensate for wrong stack height.

Verify the initial 6 mm PCB-to-plate gap against dome preload. Allow the controller down to approximately z=-8.1 and the complete protected cell at z=-11.144…-4.456. The rear USB opening is centered at x=18.6465, z=-5; a real data extension plug must fit the left-facing controller port. The tray plate needs a case-specific support and retention design. Keep metal away from the antenna region x=268…285, y=79…91 and test BLE in the finished case.

The original 299×108.6 mm one-piece base needs a 320 mm-class printer or service. The provided STL has no validated split-print joints. Calibrate PETG/ABS/ASA shrinkage and insert fit before printing a full case. The own-case plate is 295×104.6×1.6 mm with eight edge boss reliefs and a right-side RF window. Eight bottom-up M2 screws (20 mm rear / 18 mm sides / 16 mm front) enter blind bezel inserts; there are no top holes. PCB support bores remain Ø3.3×4.5 mm. See the [soldering guide](soldering-guide.md) for exact insert and head limits.
