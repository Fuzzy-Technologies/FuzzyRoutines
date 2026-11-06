<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 实用模糊计算场景一览

本文是待审译稿。[英文原文](workflow-scenario-map.md)为
[功能项 #368](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/368)
确定了十个场景。下列输入均为合成数据。部分场景沿用链接指南中的可运行模型；
其余场景给出后续示例的参考用例。预期输出用于验收计算结果，并不证明模型适用于
实际决策。隶属度不是事件概率。


| 场景              | 能力与参考                                                                       | 合成输入和预期结果                                                                                           | 图表或报告                                          |
|-----------------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|------------------------------------------------|
| 1. 测量值分级        | [标量语言尺度][temperature]                                                       | 温度为 24 °C 时，`Comfort = 2/3`，`Warm = 1/8`。选中 `Comfort`，同时保留两个隶属度。                                    | 在两条隶属度曲线上标出测量点。                                |
| 2. 风险评分         | [允许拒绝匹配的模糊化][severity]                                                      | 严重程度指数为 65（满分 100）时，`Moderate` 的隶属度为 0.4。置信度阈值为 0.45 时不匹配任何语言项，但保留隶属度。                              | 对照显示各隶属度和阈值。此例演示如何按规则处理已有评分。                   |
| 3. 告警分流         | [模糊集的有向差][alert]                                                            | 在 100 °C 时，警告和严重告警的隶属度分别为 1 和 0.5。扣除严重告警后的警告隶属度为 `min(1, 1 − 0.5) = 0.5`。                           | 绘制警告、严重告警和求差后的曲线。此例演示合成监控数据的分流。                |
| 4. 风扇控制         | [Mamdani 激活、聚合与重心法][inference]                                              | 归一化散热需求为 0.25 时，两条斜坡规则的激活强度分别为 0.75 和 0.25。用最小值激活、最大值聚合后，重心为 `37/96`，约占控制范围的 38.54%。                | 给聚合曲线下方着色并标出重心。实际设备约束需另行处理。                    |
| 5. 多准则评分        | [显式加权的 Sugeno 推理][inference]                                                | 两项输入 0.25 和 0.75 给出前件隶属度 0.75 和 0.25。规则权重为 0.5 和 1 时，归一化强度为 0.6 和 0.4，后件输出 0.2 和 0.625 得到评分 `0.37`。 | 显示两条规则各自的贡献。评分由模型定义。                           |
| 6. 传感器读数质量      | [隶属度组合][sensors]                                                            | 当 80 °C 和 10 mm/s 对应的准则隶属度为 0.5 和 0.75 时，取最小值得到 0.5，取乘积得到 0.375。                                    | 对照各项隶属度与两种计算结果。这些数值表示对所选准则的符合程度，不代表校准结果或故障率。   |
| 7. 批量标注         | [显式调用 NumPy 进行批量模糊化][batch]                                                 | 历史尺度的输入 `[0, 0.3, 0.5, 0.7, 1]` 按行得到标签 `[Min, Low, Med, High, Max]`。                                | 显示每行的隶属度和标签掩码。文件输入输出见计划任务 [#391][batch files]。 |
| 8. 神经网络预处理与输出解码 | [固定编码与留出集示例][neural]                                                        | 输入 `(0.37, 0.63)` 的参考评分为 `0.4795`，编码为 `Med` 的重心 0.5。对于记录的预测值 0.4705，固定解码器给出 `Med`。                  | 显示输入编码和输出解码。该预测值是一次参考运行的记录，不是跨平台训练的验收目标。       |
| 9. 规则诊断         | 已有[标量推理跟踪][inference]；结构检查见计划任务 [#408][rule diagnostics]。                   | 两条规则名称不同，前件、后件及权重 1 均相同，两者的激活强度均为 0.75。后续诊断示例应指出这对冗余规则。                                             | 在报告中标出两个规则名称。前件部分重叠本身不说明规则有误。                  |
| 10. 项目与图表复用     | 已有[图表生成脚本][figures]；[项目还原][project restore]和[基于项目绘图][project figures]仍在计划中。 | 还原包含[历史尺度][scale]的样例项目后，`x = 0.2` 仍选中 `Low`，隶属度为 0.5。只改变配色时，各项隶属度保持一致。                              | 对照还原前后的隶属度，并在无图形界面的环境中按新配色绘图。                  |


现有指南使用 Python API 和仓库内脚本。可移植模型、[安装后的 CLI][installed CLI]、
文件工作流与[诊断导出][diagnostic export]由[标量示例][scalar recipes]和
[进阶示例][advanced recipes]任务交付。验收数据应覆盖上述输出及适用的边界和未匹配
情况。图表通过相应版本的脚本或命令复现。神经网络示例应遵守
[ADR-0019](../adr/0019-optional-neural-integration-example.md)中的数据划分和随机种子设置。

[temperature]: ../site/content/zh-CN/guides/temperature.md
[severity]: ../site/content/zh-CN/guides/risk.md
[alert]: ../site/content/zh-CN/guides/alarm.md
[inference]: ../site/content/zh-CN/guides/inference.md
[sensors]: ../site/content/zh-CN/guides/sensors.md
[batch]: ../site/content/zh-CN/guides/numpy-batches.md
[neural]: ../site/content/zh-CN/guides/neural-integration.md
[figures]: ../site/content/zh-CN/guides/figures.md
[scale]: ../site/content/zh-CN/guides/universal-fuzzy-scale.md
[rule diagnostics]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/408
[project restore]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/387
[project figures]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/395
[installed CLI]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/390
[batch files]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/391
[diagnostic export]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/410
[scalar recipes]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/417
[advanced recipes]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/418
