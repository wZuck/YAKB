# Reviewed EC driver patch

[简体中文](README.zh-CN.md)

The west manifest retains upstream revision `bcb61bdee0a548976bea8f376f8cdec6b4ffd5fe`. Before building either image, run `python3 scripts/prepare_firmware.py --workspace /absolute/west-workspace` from the YAKB repository. It verifies the commit and exact before/after hashes, applies the patch once, and copies the shield configuration. Repeated preparation is safe; unexpected edits fail.

The patch restores fast polling on the first raw transition, preserves the two-frame press filter, and restarts idle timing when an unconfirmed pulse disappears. It also rejects equal/reversed calibration endpoints instead of dividing by zero. YAKB uses 4/8/12 ms polling waits, cooperative priority `15` (actual Zephyr priority `-1` with 16 cooperative levels), and enabled kernel assertions.

The CI workflow builds both images and compiles the actual patched read/normalize/poll functions with mocked ADC/GPIO inputs. It exercises 960 phase/frame combinations, 60-key masks/presses/releases, transient recovery and invalid calibration. This is a logic regression, not a physical latency or current measurement. The original source keeps its upstream SPDX/license notices; the patch is supplied separately rather than silently changing the pinned revision.

The calibration SNR estimate floors its denominator at one ADC count when 20 identical low samples yield zero noise; the measured noise remains unchanged. Tests extract the actual upstream `sample()` and `calibrate()` functions and exercise constant low/high input under the undefined-behavior sanitizer.
