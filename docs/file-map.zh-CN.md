# 文件版本与装配选择

[English](file-map.md) · [B1.1 装配](modular/README.zh-CN.md)

当前整机版本为 **B1.1**，由未改动的 A0 感应主板、上框、定位板，加 B1 系列模块化硬件组成。文件名中的 `B1` 是系列标识；FPC / 外壳接口修订为 B1.1。刚性小板未改铜，原生标题保留 B1。不要把文件名统一改版本号后混用旧加工文件。

| 文件组 | 当前用途 / 规则 |
| --- | --- |
| `design/yakb.json`、`scripts/circuit.py`、`hardware/YAKB.*` | A0 共享主板和机构基准。原理图与基础 BOM 仍画有 U1 模块；B1 主板 U1 只接转接板 |
| `hardware/BOM.csv` | A0 基础板 BOM，不能单独作为 B1 采购 / 实装清单 |
| `hardware/modular/BOM-B1-complete.csv` | B1 合并电子清单：46 个实装板位 / 接线位置、1 条 FPC、1 个 U1 禁装项、60 个免焊电极；JMAIN 数量 1 表示一组 24 根针 |
| `hardware/modular/BOM-B1.csv` | 模块与外壳增量清单；补齐连接器、紧固件、后舱和试件信息，不是完整主板 BOM |
| `design/modular.json`、`design/fpc-interface.json` | B1.1 模块位置、USB / FPC 尺寸合同；物理插接仍待实配 |
| `hardware/modular/YAKB-controller-B1.*` / `YAKB-interposer-B1.*` | 两张 B1 刚性小板。唯一 nice!nano 在载板；转接板 JF1 / R1 朝主板 |
| `hardware/modular/YAKB-shaped-FPC-B1.*` | B1.1 全长定制 FPC。不是通用直 FFC；24 路 A:n→B:25−n |
| `hardware/modular/YAKB-FPC-coupon-B1.*` | 仅台架试片，两插入端相距 25 mm；不能装整机代替长 FPC |
| `hardware/modular/*-netlist.csv` | 从已保存原生 PCB 提取的逐焊盘表，含实际 NC 名称；不是未布线中间表 |
| `fabrication/YAKB-A0-gerbers.zip` | B1 共用的四层主板加工包；板厚 1.6 mm |
| `fabrication/modular/*` | 两张 1 mm 双层刚性板、0.20 mm 单铜层全长 FPC / 短试片的独立包；FPC 端部补强总厚 0.30±0.05 mm，不能按默认双层 FR4 下单 |
| `mechanical/modular/assembly_B1.step` | 当前整机总装；主板上无原 U1 MCU |
| `mechanical/modular/case_base_B1*.stl`、`pod_lid_B1.stl` | 当前单仓 / 三仓底壳和后舱盖，必须配套 |
| `mechanical/case_bezel.*`、`plate_case.*`、`niz_fit_coupon.*` | A0 / B1 共用上框、定位板与 NiZ 试片 |
| `mechanical/modular/rear_pod_fit_coupon.*` | 从当前底壳裁出的后舱试件，配同一舱盖；不是独立成品外壳 |
| `mechanical/modular/*-native.step` | KiCad 板 / 器件输出；软板为均匀 0.20 mm 板厚，不含实际端部补强 |
| `mechanical/modular/shaped_fpc_envelope.step`、`fpc_mating_coupon_envelope.step` | 包含 0.30 mm 端部补强厚度的全长 / 短片机械包络 |
| `mechanical/case_base*`、`assembly.step`、`module_envelope.step`、`usb_plug_envelope.step` | A0 历史装配；主控在右前下方，USB 延长及固定结构未完成，不作为 B1 壳体文件 |
| `hardware/soldering/b1/`、`assets/modular/` | 当前 B1.1 指南与实际数据渲染 |
| `hardware/soldering/`、根 `assets/` 的旧整机图 | A0 历史指南 / 基础板位图；B1 指南另生成正确 21 步编号的共用主板图 |
| `firmware/prebuilt/yakb-a0*.uf2` | A0 / B1 共用；GPIO / 矩阵未改，保留构建名，新增滤波后重新校准 |
| `reports/modular*` | 当前模块检查；根主板、电气、机构和电池报告描述 A0 共享基准，须连同模块报告阅读 |

坐标规则：PCB、JSON、CSV 和构造报告为 x 向右、y 向使用者、z 向上；交付 STEP / DXF 为 X 向右、Y 向后、Z 向上，即 Y=-y。打印底壳 / 舱盖 STL 还加了落床旋转；不能拿打印 STL 直接套装配坐标。主板焊接背面图已镜像，小板平面图为原生顶视图。

A0 主体平面包络 299×108.6 mm，B1.1 增加左后舱后最大为 299×136.6 mm；主体前高为 21.4 mm，主体后高 25.1 mm，均不含键帽 / 脚垫，后舱另有局部包络。电池研究的混合使用天数、B1 连续活动小时数采用不同假设，不能直接比较或当成实测。

[实物验收表](modular/qualification-checklist.csv)仍全为待测；原生文件检查不会自动将其改成通过。
