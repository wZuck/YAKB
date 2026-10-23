# YAKB — Yet Another KeyBoard


> **当前推荐：B1.1 独立主控方案。** 主控移到后左独立载板，USB 从左侧直接插入；原主板 U1 只装无源转接板。请先看 [B1 结构、PCB、FPC 与验证边界](docs/modular/README.zh-CN.md) 和 [B1 焊接工作台](hardware/soldering/b1/index.html)。下方 A0 图表保留作基础设计参考。

![YAKB B1](assets/modular/B1-closed.png)


[A0 历史版焊接工作台](hardware/soldering/index.html)：18 步高亮定位图、元件筛选、完成度保存、图片放大与打印。

[English](README.md) · [中文设计说明](docs/design.zh-CN.md) · [焊接与装配顺序](docs/soldering-guide.zh-CN.md) · [兼容性](docs/compatibility.zh-CN.md)

NiZ 静电容机构、60 键 HHKB 配列、6u 空格、蓝牙 / USB、内置电池；采用 **nice!nano v2 / nRF52840 + ZMK 静电容扫描模块**，优先使用成品主控、SOIC 和 0805 手焊封装。

这是 **A0 工程原型设计**。检查记录见 [reports](reports/)。尚未打板、测量真实轴体、装配或测量续航；文件检查通过不代表实物性能已经验证。采购、完整定位板加工和整机制造前，应先完成 NiZ / 卫星轴试片与小矩阵电气验证。

![YAKB 工程概览](assets/design-overview.png)

| 项目 | 本版选择 |
| --- | --- |
| 配列 | 固定 60 键；Control 在 Caps 位置；分裂右 Shift + Fn；非对称底行；中心十字 6u 空格 |
| 机构 | NiZ 轴壳 / MX 十字滑块 / 消音圈 + 独立胶碗 + 感应锥簧 |
| PCB | 285.0 × 94.6 × 1.6 mm；GH60 / Lot60 参考安装孔槽；四层感应板 |
| 定位板 | 14.0 mm、R0.5 起始开孔；1.6 mm 厚；另附 13.9 / 14.0 / 14.1 mm 试片 |
| 主控 | 可更换 nice!nano v2；通过 2.54 mm 通孔焊接；无需手焊 nRF52840、晶振或射频匹配 |
| 模拟前端 | 2 × CD74HC4051M96、1 × OPA350UA、1 × AO3401A；阻容采用 0805 手焊焊盘 |
| 电池 | 带保护 1S LiPo，1000 mAh 为计算基准；包含保护板及线出口后的外包络 ≤ 60 × 35 × 5.5 mm |
| USB | B1 直接连接后左独立主控；A0 内部延长线方案保留为历史参考 |
| 自有打印壳 | 299 × 108.6 mm；底壳、HHKB 上框、STEP / STL、总装 STEP；约 1.95° 浅楔形底面，R8 圆角与内收下裙 |
| 其他外壳 | GH60 / Poker 托盘体系为兼容目标；PH60 HHKB 6u 为打印壳复用候选；均须核对实际型号 |

## 文件入口

- [KiCad 原理图](hardware/YAKB.kicad_sch)、[PCB](hardware/YAKB.kicad_pcb)、[BOM](hardware/BOM.csv)、本地封装库 `hardware/YAKB.pretty/`。
- [尺寸与配列源数据](design/yakb.json)、[逐键坐标](design/key-map.csv)、[主控引脚表](design/pin-map.csv)。
- [总装 STEP](mechanical/assembly.step)、[打印底壳](mechanical/case_base.stl)、[HHKB 上框](mechanical/case_bezel.stl)、[NiZ 试片](mechanical/niz_fit_coupon.stl)。
- [自有壳定位板 DXF](mechanical/plate_case.dxf)、[托盘外形定位板 DXF](mechanical/plate_tray.dxf)，同目录提供 STEP。DXF 单位为 mm，`REFERENCE` 层不能用于切割。
- [固件配置](firmware/)、[复现方法](docs/reproduce.zh-CN.md)、[来源与固定版本](docs/sources.md)。

**兼容性有明确边界：** 60% 外壳没有统一的内部电池净高、USB 座和安装方式。该 PCB 外形及孔位参考不意味着可以直接塞入全部主流外壳；金属壳还需要射频窗口。`plate_tray` 也不能凭外轮廓相近便当作整套装配已兼容。详见兼容性表。

本版没有每键二极管、热插拔座、RGB、屏幕或独立 USB 控制器。共 60 个感应单元和 40 个板上元件 / 模块 / 接线位置；成品主控内部元件不计入用户手焊工作量。

原始 YAKB 文件采用 MIT；从 Tako 复用的封装保留原许可证。PH60、Lot60、HSKB 等的具体参考范围及许可证见 [来源说明](docs/sources.md)。

[![焊接工作台界面](assets/soldering-workbench.png)](hardware/soldering/index.html)

原生检查结果：**ERC 0 项、DRC 0 项、未连接网络 0 项、原理图/PCB 一致性差异 0 项**。普通版和校准版固件均已编译。见[加工文件](fabrication/)、[外壳改版记录](docs/case-design.zh-CN.md)及 [KiCad 封装许可](licenses/KiCad-library-notice.md)。

[复核与修复记录](docs/review-fixes.zh-CN.md) · [电气、蓝牙干扰和功耗估算](docs/electrical-analysis.zh-CN.md)

外壳现为底部隐藏螺丝，正面无开孔；全部设计图来自当前 PCB/STEP/DXF。USB 与 BLE 均已编译启用，Fn+5 / Fn+6 选择输出。

[多电池选型与实际三仓底壳](docs/battery-options.zh-CN.md).

[库存对照与采购建议](docs/inventory-review.zh-CN.md)。

[外壳方向与 USB 装配状态](docs/assembly-interface.zh-CN.md)。
