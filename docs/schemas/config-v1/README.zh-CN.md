<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 可移植模糊配置示例

[English](README.md) · [Русский](README.ru.md)

[ADR-0021](../../adr/0021-versioned-project-configuration.md) 提出了
[版本 1 的 JSON Schema](../../../fuzzyroutines/config-v1.schema.json)。
安装 `fuzzyroutines[config]` 后，可以用
[`LoadModel`](../../site/content/zh-CN/api/modern/configuration.md) 读取独立模型示例，
再用 `DumpModel` 生成规范化字节。文件由调用方打开。
项目示例展示内嵌模型、呈现设置和求值场景。`LoadModel` 接受独立模型文档。

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
调用 `LoadModel` 时会在 `/scales/score/terms/0/membership` 报错，
因为该模型中没有 ID 为 `missing` 的隶属函数。

## YAML 项目验证

可选依赖组 `fuzzyroutines[yaml]` 提供 YAML 解析器。安装验证使用
`fuzzyroutines[config,yaml]`，同时检查解析、本地 v1 架构和项目语义。
YAML 与 JSON 使用相同的项目字段和引用作用域。标签、锚点、别名、
合并键和重复键都会被拒绝。`include` 等项目字段也无法通过 v1 架构验证。
测试确认转换会保留数字写法、Unicode 字符和数组顺序。

项目的公共入口由 [#387](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/387) 单独跟踪。
