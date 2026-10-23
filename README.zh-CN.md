# YAKB — Yet Another KeyBoard

[English](README.md) · [B1.1 焊接工作台](hardware/soldering/b1/index.html) · [完整装配说明](docs/modular/README.zh-CN.md) · [文件版本表](docs/file-map.zh-CN.md)

当前整机方案为 **B1.1 工程原型**：NiZ 静电容机构、60 键 HHKB 配列、中心十字 6u 空格、nice!nano v2 / nRF52840 与 ZMK，支持 USB / BLE 双模和带保护 1S 电池。

主控位于后左独立载板，USB-C 从左侧面直接插入；主板原 U1 位置只接无源转接板，**禁止再安装第二块主控**。PCB、定位板、外壳、加工文件和渲染均已交付，尚未完成实物装配、噪声、无线、温升或续航验证。先完成 NiZ / 稳定器试片、短 FPC 与后舱试件，再制造整机。

![B1.1 实际 CAD 总装；键帽和模块为净空包络](assets/modular/B1-closed.png)

| 项目 | B1.1 当前定义 |
| --- | --- |
| 配列 | 固定 60 键，Control 在 Caps 位置，分裂右 Shift + Fn；左挡块 1.5u、右挡块 2.5u；6u 空格稳定器中心距 95.25 mm |
| 机构 / 定位板 | NiZ 轴壳、MX 十字滑块、消音圈、独立胶碗和感应锥簧；1.6 mm 定位板、14.0 mm R0.5 起始孔；须用最终材料试片确认 |
| 感应主板 | 沿用 A0 四层板，285 × 94.6 × 1.6 mm；U1 不装主控 |
| 小板 / FPC | 82 × 24 × 1 mm 主控载板、40 × 19 × 1 mm 转接板；24 路定制异形 FPC，Molex 200528-0240 插座 |
| 手焊 | SOIC、0805、通孔为主；1 mm 间距 FPC 插座需助焊剂与放大检查；无需手焊 MCU、晶振或 RF 网络 |
| 电源 | 带保护 1S，默认约 100 mA 充电，BOOST 不桥接；多芯仅用厂家成组的 1S2P / 1S3P 单保护板电池包 |
| USB / 蓝牙 | USB 直接接载板上的 nice!nano；Fn+5 选 USB、Fn+6 选 BLE，一次向一个端点输出 |
| 外壳 | 专用 B1 底壳 + 后舱盖，共用 A0 HHKB 上框和定位板；最大平面包络 299 × 136.6 mm，左后舱局部增加 28 mm 深度；正面无螺丝 |
| 外壳兼容性 | 主板孔槽参考 GH60 / Lot60；B1 后舱不能直接装入所有 GH60 / Poker 商用壳，须单独适配 |

B1.1 有 **46 个实装板位 / 接线位置 + 1 条 FPC**，另列 1 个主板 U1 禁装项和 60 个免焊感应单元。没有每键二极管、热插拔座、RGB、屏幕或独立 USB 控制器。

文件入口：

- [整机电子 BOM](hardware/modular/BOM-B1-complete.csv)、[模块 / 外壳增量 BOM](hardware/modular/BOM-B1.csv)、[逐针 FPC 表](hardware/modular/FPC-pinout.csv)。电子 BOM 不包含电池、轴体和外壳紧固件；这些按装配说明和增量 BOM 核对。
- [主板 PCB](hardware/YAKB.kicad_pcb)、[主板原理图](hardware/YAKB.kicad_sch)、[主控载板](hardware/modular/YAKB-controller-B1.kicad_pcb)、[转接板](hardware/modular/YAKB-interposer-B1.kicad_pcb)、[定制 FPC](hardware/modular/YAKB-shaped-FPC-B1.kicad_pcb)。主板文件仍保留 A0 原始主控符号，B1 实装以合并 BOM 为准。
- [B1 总装 STEP](mechanical/modular/assembly_B1.step)、[单仓底壳 STL](mechanical/modular/case_base_B1.stl)、[三仓底壳 STL](mechanical/modular/case_base_B1_three_bay.stl)、[后舱盖](mechanical/modular/pod_lid_B1.stl)、[共用 HHKB 上框](mechanical/case_bezel.stl)。
- [自有壳定位板 DXF](mechanical/plate_case.dxf)、[NiZ 试片](mechanical/niz_fit_coupon.stl)、[短 FPC 加工 ZIP](fabrication/modular/YAKB-FPC-coupon-B1.zip)、[后舱打印试件](mechanical/modular/rear_pod_fit_coupon.stl)。DXF 单位 mm，`REFERENCE` 层不切割。
- [接口修正及验收表](docs/modular/interface-review.zh-CN.md)、[固件与烧录](firmware/README.zh-CN.md)、[复现](docs/reproduce.zh-CN.md)、[来源与许可证](docs/sources.md)。

原生电气报告、选定实体净空检查、加工 ZIP 和渲染文件哈希均有检查脚本。检查范围与实物待测项见 [reports](reports/) 和[一致性复核](docs/consistency-review.zh-CN.md)；文件通过不代表实物性能通过。

A0 是共享主板、上框和定位板的基础版本。其[历史焊接页](hardware/soldering/index.html)、[外壳记录](docs/case-design.zh-CN.md)、[基础电气分析](docs/electrical-analysis.zh-CN.md)及[多电池研究](docs/battery-options.zh-CN.md)有明确版本范围；A0 底壳与未完成的 USB 延长结构不用于当前 B1 整机。

原始 YAKB 文件采用 MIT；复用的 Tako / KiCad 库材料保留各自许可，具体参考范围见来源说明。
