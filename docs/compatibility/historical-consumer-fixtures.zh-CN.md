<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 历史模糊尺度的兼容性测试

[English](historical-consumer-fixtures.md) · [Русский](historical-consumer-fixtures.ru.md)

这些用例用于验证应用从 FuzzyRoutines 1.x 升级到 2.x 时调用历史尺度的行为。
应用代码和数据均保留在各自的仓库中。各应用自行确定归一化方式、决策规则和端到端验收标准。

- **TKSBrokerAPI**：重放 `RiskLong` 和 `RiskShort` 的 30 个公开测试用例，
  比对归一化坐标、保留四位小数的百分比及选中的语言项。
  另有一组 [迁移基准](../migration/consumer-scale-boundary.md)，记录了 27 个合成用例在
  1.0.3 和 2.0.0 中的结果。
- **PriceGenerator**：示例将 10000 到 10100 之间的虚构整数报价映射到单位区间。
  10000、10023 和 10100 分别选中 Min、Low 和 Max，其中 10023 位于 Low 的平台边界。
- **FMA**：示例将区间 −50 到 50 内的虚构特征值 −33、0 和 27 分别映射为
  0.17、0.5 和 0.77，对应 Min、Med 和 High。0.17 处 Min 的隶属度约为
  0.00213。若应用显式设置 0.01 的最低置信度，分类器会返回无匹配结果。

此处没有获准使用的 PriceGenerator 或 FMA 代表性输入，也未验证这两个应用的实际归一化规则。
合成用例检验的是尺度本身，无法据此确认应用已完成升级或交易决策保持一致。

归一化坐标、标签和语言项顺序必须完全一致。隶属度的绝对容差为 `1e-12`，
相对容差为零。2.x 的重心计算修正另行评估。用例文件和执行命令见
[英文说明](historical-consumer-fixtures.md)。
