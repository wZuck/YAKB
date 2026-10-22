# 复现、检查和固件

[English](reproduce.md) · [设计](design.zh-CN.md) · [焊接工作台](../hardware/soldering/index.html)

原生 `hardware/YAKB.kicad_pcb` 是已保存布线的交付源文件。机械源数据在 `design/yakb.json`，电路元件与网络在 `scripts/circuit.py`。生成器用于修改设计；**重新执行 PCB 生成器会覆盖现有布线**，先复制工作目录或建立 Git 分支。

## 工具版本

- KiCad 10：原理图、PCB、ERC、DRC、Gerber；脚本使用 KiCad 自带 Python/`pcbnew`/wx。
- Python 3.13 + `requirements-cad.txt`：CadQuery 2.8、ezdxf、Matplotlib、VTK（由 CadQuery 环境带入）。
- FreeRouting 2.5.0 + Java 25：矩阵预布线后，使用电子区交换代理辅助布线；代理不是制造 PCB。
- ZMK 固定提交、EC 模块固定提交和冻结依赖见 `firmware/config/west.yml`、`firmware/west-lock.yml`。

本机 KiCad 命令路径如下；其他系统改用对应 `kicad-cli` 和 KiCad Python。

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-cad.txt
.venv/bin/python scripts/export_geometry.py --kicad-cli /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
.venv/bin/python scripts/generate_mechanical.py
.venv/bin/python scripts/analyze_electrical.py
.venv/bin/python scripts/study_batteries.py
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 scripts/export_pad_map.py -ApplePersistenceIgnoreState YES
.venv/bin/python scripts/render_cad.py --blender /absolute/path/to/blender --samples 96 --width 3200
.venv/bin/python scripts/render_design.py
```

机械生成会更新 STEP/STL/DXF 和 `reports/mechanical.json`。Cycles 渲染读取保存的 STEP 网格与 KiCad GLB；原生板上器件使用库模型，键帽、主控和电池是明确交付的 CAD 包络，不能据此宣称厂商零件已试装。

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export netlist --format kicadxml -o reports/schematic.net.xml hardware/YAKB.kicad_sch
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc --format json -o reports/erc.json hardware/YAKB.kicad_sch
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc --schematic-parity --format json -o reports/drc.json hardware/YAKB.kicad_pcb
.venv/bin/python scripts/verify_design.py
```

`verify_design.py` 核对 60 键位置、实际导出原理图网络、固件映射和机械包络。它不代替原生 DRC、模拟采样和实物测试。

恢复完整已检查布线时，用 KiCad Python 依次运行 `scripts/generate_pcb.py` 和 `scripts/apply_routing.py`。前一步建立四层 PCB 与原生封装，后一步从 `design/routing.json` 恢复全部铜层并绑定原理图 UUID。恢复前校验 PCB 几何和电路的 SHA256；尺寸、孔位、配列或引脚改变后拒绝回放旧布线，必须重新布线后用 `export_routing.py` 更新。不要在旧布线上再次叠加铜线。实际执行过“生成 → 恢复 → 原生检查”验证。

原生 DRC 建议增加 `--schematic-parity`，本次包括封装库一致性、原理图配对、未连接网络和几何规则在内均为 0 项。`reports/pcb-connectivity.json` 记录 309 个实际连接引脚及四层板信息；8 个显式 NC 引脚另外保留原理图生成的唯一网络名。`fabrication/gerbers/` 是完整四层和钻孔输出，加工要求见 [fabrication/README.zh-CN.md](../fabrication/README.zh-CN.md)。

更新交互焊接指南：

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 scripts/export_pad_map.py -ApplePersistenceIgnoreState YES
.venv/bin/python scripts/generate_soldering.py
python3 -m http.server 8769 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8769/hardware/soldering/`，或直接用浏览器打开 HTML。页面无外部脚本/CDN，也不需要上传 BOM。搜索、工艺筛选、进度保存、图片放大和打印均在本地完成。浏览器进度不等于首件验收记录。

## 已编译固件

`firmware/prebuilt/yakb-a0.uf2` 是正常键盘版，`yakb-a0-calibrator.uf2` 启用 EC 校准工具。校验值在同目录 `SHA256SUMS`。按控制器文档进入 UF2 bootloader 后复制相应文件；电池先断开。上板后先确认 3.3V 和前端供电时序，再测试 EC。

在独立目录复制 `firmware/config/` 为 `config/`，将冻结清单 `firmware/west-lock.yml` 复制为 `config/west.yml`，然后：

```sh
west init -l config
west update
```

先回到 YAKB 仓库执行 `python3 scripts/prepare_firmware.py --workspace /absolute/west-workspace`，再编译两种镜像；冻结清单不会自动应用本地补丁。

本次实际使用镜像：

```
zmkfirmware/zmk-build-arm@sha256:edb1c953438c6f720ddb79c3762f3972013b7fbbaf4fff3592fc869983e7afc5
```

将独立工作区挂载为 `/work`，在镜像中运行：

```sh
west build -p always -s zmk/app -d build/yakb -b nice_nano@2.0.0/nrf52840/zmk -- -DZephyr_DIR=/work/zephyr/share/zephyr-package/cmake -DZMK_CONFIG=/work/config -DSHIELD=yakb
west build -p always -s zmk/app -d build/yakb-calibrator -b nice_nano@2.0.0/nrf52840/zmk -S enable_ec_calibrator -- -DZephyr_DIR=/work/zephyr/share/zephyr-package/cmake -DZMK_CONFIG=/work/config -DSHIELD=yakb
```

SDK 0.16.9 / GCC 12.2；本次正常版 Flash 231056 B、RAM 48048 B；校准版 Flash 262676 B、RAM 56368 B。构建日志保存在 `reports/`。在 macOS/Colima 上使用可挂载的用户目录工作区，不能假定 macOS `/tmp` 已映射进虚拟机。

先使用少量装好的机构观察噪声和按下/释放差值，其余未装位置的响应不要当成成品结论。正式 60 键全部安装后，再逐键校准、保存并断电重启验证。深睡眠默认关闭，12 ms 轮询不是独立外部唤醒电路。固件编译成功不等于 ADC 参数、回弹和蓝牙功耗已经上板验证。

## 输出与首件

加工前重新运行检查，确认版本、边界、层数、板厚、孔槽和 Gerber。静电容电极不要覆锡或随意添加铜皮。先验证同材料 NiZ/稳定器试片，再制造完整定位板；首板完成电源、波形、校准、蓝牙、电池和温升测试后再批量加工。

## 发布验证与真实渲染

渲染额外需要 Blender 4.5 LTS；本次为 4.5.3、Cycles 96 samples、3200 px、AgX 与软光源。模型来自保存的 STEP 和 KiCad 原生 GLB，二维来自 DXF/实际铜箔/实际截面。图注区分真实几何和包络。KiCad 官方 3D 库必须安装。

```sh
# Run the two native exporters with KiCad's Python first.
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 scripts/export_routing.py -ApplePersistenceIgnoreState YES
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 scripts/export_pad_map.py -ApplePersistenceIgnoreState YES
.venv/bin/python scripts/export_fabrication.py --kicad-cli /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
.venv/bin/python scripts/generate_soldering.py
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 scripts/verify_hardware.py -ApplePersistenceIgnoreState YES
.venv/bin/python scripts/verify_design.py
.venv/bin/python scripts/analyze_electrical.py
.venv/bin/python scripts/test_ec_driver.py --workspace /absolute/west-workspace
.venv/bin/python scripts/package_firmware.py --workspace /absolute/west-workspace
.venv/bin/python scripts/verify_release.py
```

修改 PCB 后，先更新原生导出和 Gerber，再重新执行本页开头的模型/图像流程，最后执行验证。三个 render-manifest 文件保存输入与输出 SHA256，来源变化会拒绝验证；渲染途中改变源文件会失败。UF2 包装核对实际驱动、DTS、对象文件时序和 ELF 有效段字节，资源用量直接读 ELF。macOS 的 ApplePersistenceIgnoreState 参数仅抑制原生 Python 的恢复窗口对话框，其他系统省略。
