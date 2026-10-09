<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 带类型的语言术语表示 {#typed-linguistic-term-representation}

## 范围 {#scope}

现代 API 将一个语言术语表示为不可变关联：

```text
LinguisticTerm(name, fuzzySet)
```

`name` 是非空字符串，按声明原样保留。`fuzzySet` 是现代 `ScalarFuzzySet`；
此表示不会静默适配历史可变 `FuzzySet` 类。

有序尺度表示为：

```text
LinguisticScale((term1, term2, ...))
```

显式元组按原样保留，不排序或归一化。它必须非空，只包含 `LinguisticTerm`，
且名称在 Unicode 不区分大小写比较下唯一。
仅大小写不同的声明，如 `Low` 和 `LOW`，会被拒绝，因为它们使不区分大小写的查找产生歧义。

`GetTermByName(termName, exactMatching=True)` 执行完整名称查找。
默认模式精确比较名称，包括大小写。传入 `exactMatching=False` 时比较 Unicode 大小写折叠后的名称。
两种模式都返回原先声明的 `LinguisticTerm` 对象或 `None`；
都不执行子串、前缀、近似或基于隶属度的匹配。

## 模糊化与置信度 {#fuzzification-and-confidence}

`Fuzzify(coordinate, policy)` 对每个术语恰好求值一次，返回 `FuzzificationResult`。
其有序 `memberships` 元组保留每个术语和隶属度，而 `confidence` 是最大隶属度，不是概率。

`FuzzificationPolicy` 使两类不确定情况都显式化：

- `minimumConfidence` 在最大隶属度小于或等于阈值时拒绝分类；
  默认零阈值拒绝零覆盖，正阈值还会拒绝接近零的覆盖；
- `tieTolerance` 定义被视为并列的、距最大值的绝对距离；
- `tiePolicy` 按声明的尺度顺序选择并列术语中的 `first`、`last` 或 `all`。

零并列容差直接比较经过验证的隶属度。
不同的 `Fraction` 隶属度仍保持不同，即使转为 `float` 后会得到相同值。
正容差采用包含边界的距离比较；有理数隶属度及有理数与浮点数混合时，
比较保留各自精确表示的值。结果与策略中记录的值绝不转换。

当两个隶属度和显式正容差均为浮点数时，既有边界舍入规则还接受
与容差相对接近的距离（`rel_tol=1e-12`、`abs_tol=0`）。
例如，即使减法发生舍入，`0.7` 和 `0.75` 在容差 `0.05` 下仍为并列。
此规则不适用于零容差或有理数依据。

即使没有匹配，完整隶属度元组仍可用。坐标必须属于每个术语的论域；
部分分数向量会明确失败。这些语义由
[ADR-0013](../../../../adr/0013-linguistic-fuzzification-policy.md) 固定。

## 尺度采样诊断 {#sampled-scale-diagnostics}

`Diagnose(analysisDomain, policy)` 在有限 `IntegrationDomain` 上计算显式、保留端点的网格。
每个术语都必须使用包含整个分析域的 `ContinuousUniverse`。
对于每个采样坐标 $x_j$，结果记录所有按顺序排列的隶属度以及

$$
c_j=\max_i\mu_{L_i}(x_j).
$$

给定显式激活阈值 $\tau$，仅当 $\mu_{L_i}(x_j)>\tau$ 时术语才激活。
没有激活术语的采样点为空缺；至少两个术语激活时为重叠。
分割质量依据使用

$$
e_j=\left|\sum_i\mu_{L_i}(x_j)-1\right|.
$$

`ScaleDiagnosticsResult` 公开每个采样点，以及覆盖度极值和均值、空缺和重叠比例、
同时激活术语数的最大值、平均及最大分割误差。
`partitionTolerance` 决定全部采样误差是否被接受。
对于声明的域、网格大小和容差，这些观测可复现，但不证明网格坐标之间的连续属性。
[ADR-0014](../../../../adr/0014-sampled-scale-diagnostics.md) 固定完整的验证依据边界。

## 兼容性 {#compatibility}

历史 `fuzzyroutines.FuzzyRoutines.FuzzyScale` 仍然可用。
其 `levels` 属性继续公开并接受原有可变字典列表，其中必须同时包含 `name` 和 `fSet` 键。
受保护的 `GetLevelByName(levelName, exactMatching=True)` 调用形式保留：
默认精确匹配完整名称，`False` 则通过历史大写映射进行不区分大小写的完整名称查找。
忽略大小写后冲突的名称会被拒绝，以保持无歧义查找。
现代类型是新增能力，不替换可变字典兼容门面。
历史 `Fuzzy()` 仍在精确并列时选择较后的级别。
现代等价方式为显式 `FuzzificationPolicy(tiePolicy="last")`，而非隐藏默认值。

## 示例 {#example}

```python
from fuzzyroutines import (
    ContinuousUniverse,
    FuzzificationPolicy,
    IntegrationDomain,
    LinguisticScale,
    LinguisticTerm,
    ScaleDiagnosticsPolicy,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
low = LinguisticTerm("Low", ScalarFuzzySet(universe, lambda value: 1.0 - value))
high = LinguisticTerm("High", ScalarFuzzySet(universe, lambda value: value))
scale = LinguisticScale((low, high))
assert scale.GetTermByName("Low") is low
assert scale.GetTermByName("high", exactMatching=False) is high
result = scale.Fuzzify(
    0.5,
    FuzzificationPolicy(tiePolicy="all", minimumConfidence=0.1),
)
assert result.confidence == 0.5
assert result.selectedTerms == (low, high)

diagnostics = scale.Diagnose(
    IntegrationDomain(0.0, 1.0),
    ScaleDiagnosticsPolicy(sampleCount=101),
)
assert diagnostics.minimumCoverage == 0.5
assert diagnostics.gapPoints == ()
```
