<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 可移植模糊配置示例

[English](README.md) · [Русский](README.ru.md)

[ADR-0021](../../adr/0021-versioned-project-configuration.md) 提出了
[版本 1 的 JSON Schema](../../../fuzzyroutines/config-v1.schema.json)。这些 JSON 文件用于说明和检验
拟议格式，可以用 JSON Schema 验证器检查。本次变更尚未为 FuzzyRoutines 添加加载接口。

- [历史通用模糊标度](fixtures/valid-historical-scale.json) 保留了五个原始语言项、
  各项系数、闭区间论域 `[0, 1]`、各项的质心积分区间，以及在最大隶属度完全相等时
  选择最后一项的规则。例如，输入为 `0.75` 时选中 `High`，隶属度为 `1`。
- [离散标度](fixtures/valid-discrete-scale.json) 只在声明的三个坐标上计算解析的
  Harrington 隶属函数。相邻坐标之间的点不属于该离散论域。
- [项目](fixtures/valid-project.json) 包含 Mamdani 模型 `centroid` 和 Sugeno 模型
  `weighted`。场景 `quarter` 选用 `weighted`，设 `risk = 0.25`；两条规则的
  激活强度分别为 `0.875` 和 `0.125`，后件值分别为 `0.25` 和 `0.625`，
  加权结果为 `0.296875`。在同一输入下，Mamdani 模型截取对称三角形的顶部，
  所得模糊集的质心为 `0.5`。图表标题、颜色和单位标签均不参与运算。

如需修改运算方式，应编辑模型定义；如需调整图表标签或颜色，应编辑
`presentation`。引用必须使用相应作用域内的 ID。例如，场景使用输入 ID
`risk`，而运行时变量名为 `Risk`。

可以用[验证命令](README.md#checking-the-files)在本地检查示例。
[可调用对象示例](fixtures/invalid-schema-callable.json) 无法通过结构验证，
因为配置不允许这种函数类型或导入路径。
[引用缺失示例](fixtures/invalid-semantic-reference.json) 能通过结构验证，
但加载时应在 `/scales/score/terms/0/membership` 报错，因为该模型中没有
ID 为 `missing` 的隶属函数。未来的加载器必须同时检查结构和引用关系。
