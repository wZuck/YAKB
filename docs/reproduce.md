# Reproduction and firmware

[简体中文](reproduce.zh-CN.md). `hardware/YAKB.kicad_pcb` is the routed native source. `design/yakb.json` holds shared dimensions and layout; `scripts/circuit.py` holds physical pins and nets. **Regenerating the PCB overwrites routing.** Work on a copy or branch.

Use KiCad 10, its bundled Python/pcbnew/wx, Python 3.13 with `requirements-cad.txt` (CadQuery 2.8, ezdxf, Matplotlib and VTK), and FreeRouting 2.5.0/Java 25 for routing interchange.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-cad.txt
.venv/bin/python scripts/generate_mechanical.py
.venv/bin/python scripts/render_cad.py
.venv/bin/python scripts/render_design.py
.venv/bin/python scripts/generate_schematic.py
.venv/bin/python scripts/generate_firmware.py
```

Generate a KiCad XML netlist into `reports/schematic.net.xml`, then run native ERC/DRC and `.venv/bin/python scripts/verify_design.py`. See the Chinese page for the exact macOS KiCad executable paths. The cross-file check covers key positions, real schematic netlist, firmware transform and selected mechanical envelopes; it does not replace native DRC or physical tests.

Run `generate_pcb.py` then `apply_routing.py` with KiCad Python to restore the checked four-layer PCB from `design/routing.json`. A geometry/circuit SHA256 check refuses stale routing after dimensions, mounts, layout or pins change. Reroute edits and refresh the snapshot with `export_routing.py`. Never overlay the snapshot onto an already routed board. A generate/restore/native-check cycle was executed successfully.

Use `--schematic-parity` for native DRC. Geometric rules, library consistency, schematic pairing and airwires are all clear. `reports/pcb-connectivity.json` records 309 connected physical pins; eight explicit NC pins retain their unique schematic net names. Four-layer Gerber/drill outputs are in `fabrication/gerbers/`; see [fabrication notes](../fabrication/README.md).

To refresh the offline workbench, run `export_pad_map.py` with KiCad Python, then `generate_soldering.py` with the CAD Python environment. Open the HTML directly or serve the repo with `python3 -m http.server 8769 --bind 127.0.0.1`. No external scripts, CDN or BOM upload are needed.

## Firmware build record

Normal and calibrator UF2 files are in `firmware/prebuilt/`, with `SHA256SUMS`. Enter the controller's documented UF2 bootloader and copy the required file with the cell disconnected. Confirm rails and amplifier timing before EC testing.

Copy `firmware/config/` to `config/` in a separate workspace, then replace its `west.yml` with the frozen `firmware/west-lock.yml`. Run `west init -l config` and `west update`. Use the build container pinned to:

```
zmkfirmware/zmk-build-arm@sha256:edb1c953438c6f720ddb79c3762f3972013b7fbbaf4fff3592fc869983e7afc5
```

Mount that workspace as `/work` and run:

```sh
west build -p always -s zmk/app -d build/yakb -b nice_nano@2.0.0/nrf52840/zmk -- -DZephyr_DIR=/work/zephyr/share/zephyr-package/cmake -DZMK_CONFIG=/work/config -DSHIELD=yakb
west build -p always -s zmk/app -d build/yakb-calibrator -b nice_nano@2.0.0/nrf52840/zmk -S enable_ec_calibrator -- -DZephyr_DIR=/work/zephyr/share/zephyr-package/cmake -DZMK_CONFIG=/work/config -DSHIELD=yakb
```

Actual toolchain: SDK 0.16.9 / GCC 12.2. Normal build: Flash 198432 B, RAM 47772 B. Calibrator: Flash 225624 B, RAM 56108 B. Logs are in `reports/`; successful compilation does not validate analog operation. On macOS/Colima, use a host workspace mounted into the VM rather than assuming `/tmp` is shared.

Observe a few assembled sensing cells first, then install and calibrate all 60 valid positions. Explicitly save and verify restoration after power cycling. Deep sleep is disabled; 200 ms polling is not an external wake circuit. Verify signal swing, noise, thresholds, preload, BLE release events, charging temperature and average cell current on the first article.

Before fabrication, rerun the checks and inspect layer count, 1.6 mm thickness, outlines, slots and manufacturing outputs. Keep EC electrodes free of added solder or arbitrary pours. Cut a final-material switch/stabilizer coupon before a complete plate.
