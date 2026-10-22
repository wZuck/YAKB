# YAKB ZMK 固件

[English](README.md) · [完整复现记录](../docs/reproduce.zh-CN.md)

主控固定为 **nice!nano v2 / nRF52840**。`prebuilt/yakb-a0.uf2` 为键盘版，`prebuilt/yakb-a0-calibrator.uf2` 为 USB CDC 校准版；SHA256 见 `prebuilt/SHA256SUMS`。两者均已编译，尚未上板测试。

使用 `config/west.yml` 固定顶层版本，`west-lock.yml` 冻结全部实际依赖。普通版与校准版共享相同的配列、主控映射、5 行/15 列扫描和 60 个有效位置。矩阵空位 mask 为 `0x0 0x2 0x4002 0x1001 0x6b73`。

## 烧录与校准

1. 断开电池，以 USB 数据线直接连接主控。按 nice!nano 文档进入 UF2 bootloader，复制校准版 UF2。
2. 确认 3.3V、Q1 门极时序和 U4 输出没有异常，再连接出现的 USB CDC 串口；选择常规 115200、8N1。CDC 是 USB 虚拟串口，速率并不决定 EC 扫描速度。
3. 输入 `ec` 并用 Tab 查看设备名，本版节点名为 `kscan0`。若固件输出不同，以自动补全结果为准。
4. 60 键正式机构装好后运行 `ec kscan0 calibration start`。低值采样时不按任何键；提示高值采样后按驱动提示逐个慢按、出现星号后释放，直至完成。
5. 运行 `ec kscan0 calibration export`，保存串口输出作为首件记录；运行 `ec kscan0 calibration save` 明确写入 Flash。
6. 断电重启，核对校准恢复；必要时运行 `ec kscan0 calibration load`。切回正常版 UF2 后再次检查所有键；不要擦除 settings 区来“更新固件”。

少量机构试装用于观察波形、噪声和趋势；完整校准流程需要所有有效位置，不能把未装键的读数当成成品结果。不要在校准过程中让电池或 USB 电源不稳定。

## 默认行为

Fn+1/2/3 选择蓝牙槽位；Fn+4 清除当前槽位配对；Fn+H/J/K/L 为方向键；Fn+Esc 进入 bootloader。默认通过 ZMK 的 USB/BLE 行为工作，细节见 `yakb.keymap`。

D19=P0.02/AIN0 是感应 ADC；D18 不用于 ADC。`power-gpios` 为低有效，控制 Q1，只切断运放供电；MUX 和 nice!nano VCC 在轮询时保留。扫描间隔初始为 4/50/200 ms，需测量实际帧率、漏首击和功耗。深睡眠禁用，当前没有独立可靠唤醒电路。

文件级检查和编译成功不代表 EC 动态范围、RF、功耗或温升已验证。每次修改传感、前端增益或机构预压后重新校准。
