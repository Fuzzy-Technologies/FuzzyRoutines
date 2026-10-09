<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 论域与支集契约 {#universe-and-support-contract}

- 状态：任务 #9 和 #67 的契约参考
- 相关 ADR：[ADR-0002](../../../../adr/0002-universe-support-semantics.md)
- 当前可执行接口：`fuzzyroutines.domain`、`fuzzyroutines.properties`
  及历史适配器 `fuzzyroutines.FuzzyRoutines.FuzzySet`

## 规范术语 {#canonical-vocabulary}

| 术语     | 含义              | 是否可以无界？             | 精确性规则               |
| ------ | --------------- | ------------------- | ------------------- |
| 论域     | 隶属函数定义模糊集的坐标集合  | 可以                  | 显式声明，绝不由采样推断        |
| 积分域    | 连续数值方法使用的有限工作区间 | 初始数值 API 中不可以       | 按集合或操作声明            |
| 模糊集的支集 | 论域内隶属度严格为正的坐标   | 可以                  | 从精确函数族几何推导，或明确标注为近似 |
| 支集闭包   | 支集相对于论域的闭包      | 可以                  | 要求声明拓扑或区间语义         |
| 模糊集的核  | 隶属度恰好为一的坐标      | 可以                  | 对于从未达到一的非正规模糊集为空    |
| 边界     | 隶属度严格介于零和一之间的坐标 | 可以                  | 模糊过渡区域，并非拓扑边界       |
| 高度     | 论域上隶属度的上确界      | 不可以；为 `[0, 1]` 内的标量 | 有证明时为精确值，否则明确标注为近似  |

历史名称 `supportSet` 仅对应**积分域**，绝不声称表示支集或支集闭包。

## 兼容示例 {#compatibility-examples}

| 隶属函数族           | 实数轴上的数学结果                                | 历史 `supportSet` 示例 | 解释           |
| --------------- | ---------------------------------------- | ------------------ | ------------ |
| 底点为 `0, 2` 的三角形 | 支集为 `(0, 2)`                             | `(-1, 3)`          | 更宽的数值积分窗口    |
| 位于 `0, 1` 的递增肩部 | 支集为 `(0, +infinity)`，核为 `[1, +infinity)` | `(0, 1)`           | 有限数值窗口，并非支集  |
| 中心位于 `0` 的高斯函数  | 支集为实数轴                                   | `(-4, 4)`          | 为数值计算选择的截断窗口 |

更改 `FuzzySet.supportSet` 必须改变历史解模糊化使用的区间，而不改变隶属函数求值器。
兼容性测试在门面委托现代域模型执行工作时保护此行为。

## 表示规则 {#representation-rule}

解析隶属函数和采样模糊集是不同的表示。
扫描网格可以回答有界的近似查询，但不能确定连续函数族的精确支集。
每个近似派生结果必须保留其生成时使用的域、分辨率或容差以及方法。

此规则防止把数值下溢、绘图边界或调用者选择的质心窗口误当作数学元数据。

## 可执行的域类型 {#executable-domain-types}

现代标量 API 提供三个不可变值对象：

```python
from fuzzyroutines import ContinuousUniverse, DiscreteUniverse, IntegrationDomain

realLine = ContinuousUniverse()
boundedUniverse = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
sampledUniverse = DiscreteUniverse((0.0, 0.5, 1.0))
integrationDomain = IntegrationDomain(0.1, 0.9).ValidateWithin(boundedUniverse)
```

`ContinuousUniverse` 仅用 `None` 表示无界端点，并显式记录端点是否包含。
`DiscreteUniverse` 要求显式、非空、严格递增且坐标各异的有限坐标元组。
`IntegrationDomain` 始终是有限闭区间，可在数值操作开始前根据连续论域验证。

`IntegrationDomain.FromLegacyInterval(...)` 和 `ToLegacyInterval()` 构成
历史 `supportSet` 元组的唯一兼容适配器。历史 `FuzzySet` 门面现在在内部保存此值对象，
而公共读取器和设置器仍保留历史元组形式。

## 可执行的派生属性 {#executable-derived-properties}

`DeriveProperties(membershipFunction, universe)` 返回两种精确结果类型之一：

- `ContinuousFuzzyProperties` 使用现代 `MembershipFunction` 或已知历史 `MFunction`
  函数族所声明的解析几何，并将集合表示为 `ContinuousInterval` 分量的不可变并集；
- `DiscreteFuzzyProperties` 对声明的 `DiscreteUniverse` 中每个坐标求值。
  在离散拓扑中，每个子集均为闭集，因此支集与支集闭包相同。

每个结果公开 `positiveSupport`、`supportClosure`、`core`、`boundary`、
`height` 和 `isExact == True`。区域裁剪到声明论域内；支集闭包在该论域的相对拓扑中计算。
因此，论域之外的支集极限点不能作为单点分量加入。

```python
from fuzzyroutines import ContinuousUniverse, DeriveProperties
from fuzzyroutines.FuzzyRoutines import MFunction

membershipFunction = MFunction("triangle", a=0.0, b=2.0, c=1.0)
properties = DeriveProperties(membershipFunction, ContinuousUniverse())

assert properties.positiveSupport.Contains(0.5)
assert properties.core.Contains(1.0)
assert properties.height == 1.0
```

`SampleProperties(membershipFunction, analysisDomain, sampleCount)` 是不同的 API，
使用不同的结果类型。`SampledFuzzyProperties` 记录有限分析域、采样点数、坐标、
隶属度及 `method="uniform-grid"`；其 `isExact` 属性始终为假。
字段命名为 `positiveSupportSamples`、`coreSamples`、`boundarySamples`
和 `heightEstimate`，使有限网格不能冒充精确连续几何。

高斯支集通过解析方式推导为实数轴，即使远处的浮点求值下溢为零也不改变此结论。
Logistic 和 Harrington 隶属函数在实数轴上的核为空，而高度为一：
它们逼近上确界，但在任何有限坐标处都不达到该值。
