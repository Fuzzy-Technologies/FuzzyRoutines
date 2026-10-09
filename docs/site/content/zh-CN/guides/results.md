<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 检查并重建结果记录 {#inspect-and-reconstruct-result-records}

结果记录保留计算的依据。通常应优先调用产生结果的函数；显式构造函数适用于在组件之间传递已经验证的记录。构造验证检查文档规定的一致性规则，不独立证明数学结论。现代记录不可变。应用应同时保存单位和模型假设。以下每个代码块都可独立运行。

## 精确连续与离散几何 {#exact-continuous-and-discrete-geometry}

```python
from fuzzyroutines import (
    ContinuousFuzzyProperties, ContinuousUniverse, DeriveProperties,
    DiscreteFuzzyProperties, DiscreteUniverse, Triangle,
)

model = Triangle(0, 1, 2)
continuous = DeriveProperties(model, ContinuousUniverse(0, 2, leftClosed=True, rightClosed=True))
continuousCopy = ContinuousFuzzyProperties(
    continuous.universe, continuous.positiveSupport, continuous.supportClosure,
    continuous.core, continuous.boundary, continuous.height,
)
assert continuousCopy == continuous and continuousCopy.isExact
discrete = DeriveProperties(model, DiscreteUniverse((0, 0.5, 1, 1.5, 2)))
discreteCopy = DiscreteFuzzyProperties(
    discrete.universe, discrete.positiveSupport, discrete.supportClosure,
    discrete.core, discrete.boundary, discrete.height,
)
assert discreteCopy == discrete and discreteCopy.isExact
assert discrete.core.Contains(1) and not discrete.positiveSupport.Contains(0)
assert discrete.boundary.points == (0.5, 1.5) and discrete.height == 1
print(continuous.height, discrete.positiveSupport.points, discrete.boundary.points)
```


连续支集为开区间 (0, 2)，其闭包为 [0, 2]。在离散论域上，支集是三个点 {0.5, 1, 1.5}，闭包与之相同。两个核均为 {1}。隶属度为零的端点属于连续支集的闭包，却不属于支集本身；离散拓扑给出不同的闭包。

## 采样性质保留其网格 {#sampled-properties-retain-their-grid}

```python
from fuzzyroutines import IntegrationDomain, SampledFuzzyProperties, SampleProperties, Triangle

sampled = SampleProperties(Triangle(0, 1, 2), IntegrationDomain(0, 2), sampleCount=5)
copy = SampledFuzzyProperties(
    sampled.analysisDomain, sampled.sampleCount, sampled.coordinates, sampled.grades,
    sampled.positiveSupportSamples, sampled.coreSamples, sampled.boundarySamples,
    sampled.heightEstimate, sampled.method,
)
assert copy == sampled and not copy.isExact
assert copy.coordinates == (0, 0.5, 1, 1.5, 2)
assert copy.grades == (0, 0.5, 1, 0.5, 0)
assert copy.coreSamples.points == (1,) and copy.heightEstimate == 1
print(copy.coordinates, copy.grades, copy.method)
```


该网格恰好采到峰值。其他网格可能漏掉窄峰，因此 `heightEstimate` 是观测值，而非精确上确界。直接构造会检查顺序、端点、区域子集和观察到的最大值；不会重新计算全部区域分类，也不证明网格等距。创建新证据时应优先使用 `SampleProperties`。

## 采样 α-截集是表格，不是区间解析解 {#a-sampled-alpha-cut-is-a-table-not-an-interval-solution}

```python
from fuzzyroutines import (
    ContinuousUniverse, IntegrationDomain, SampleAlphaCut,
    SampledAlphaCut, ScalarFuzzySet, Triangle,
)

fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 2, leftClosed=True, rightClosed=True), Triangle(0, 1, 2))
cut = SampleAlphaCut(fuzzySet, 0.5, IntegrationDomain(0, 2), sampleCount=5)
copy = SampledAlphaCut(
    cut.alpha, cut.analysisDomain, cut.sampleCount, cut.coordinates,
    cut.grades, cut.cutSamples, cut.method,
)
assert copy == cut and not copy.isExact
assert copy.cutSamples.points == (0.5, 1, 1.5)
print(copy.alpha, copy.cutSamples.points)
```


弱截集包含隶属度为 0.5 的边界。这个三角形的解析截区间为 [0.5, 1.5]，但 `SampleAlphaCut` 只返回符合条件的网格坐标。构造函数根据全部传入隶属度检查截集。对于手动传入的表格，来源标签不能独立确立等距采样。参见 [α-截集](alpha-cuts.md)。

## 分类保留全部隶属度及选择策略 {#a-classification-keeps-all-grades-and-its-selection-policy}

```python
from fuzzyroutines import (
    DiscreteUniverse, FuzzificationPolicy, FuzzificationResult,
    LinguisticScale, LinguisticTerm, ScalarFuzzySet, TermMembership, Triangle,
)

term = LinguisticTerm("Preferred", ScalarFuzzySet(DiscreteUniverse((0, 1, 2)), Triangle(0, 1, 2)))
scale = LinguisticScale((term,))
assert scale.GetTermByName("Preferred") is term
assert scale.GetTermByName("PREFERRED", exactMatching=False) is term
assert scale.GetTermByName("Missing") is None
policy = FuzzificationPolicy(tiePolicy="all")
result = scale.Fuzzify(1, policy)
copy = FuzzificationResult((TermMembership(term, 1),), 1, policy, (term,), (term,))
assert copy == result and copy.isMatch and not copy.isTie
assert copy.memberships[0].grade == copy.confidence == 1
print(copy.selectedTerms[0].name, copy.confidence)
```


`memberships` 保留完整的有序词项向量；`tiedTerms` 和 `selectedTerms` 说明保留了哪些最大值、又选中了哪些词项。置信值是最大隶属度，不是概率。默认阈值为零时，零覆盖产生无匹配结果；隶属度等于 `minimumConfidence` 时同样无匹配。参见[严重程度与拒绝分类](risk.md)以及[并列结果](scale-audit.md)。

## 结合采样限制读取尺度诊断 {#read-every-scale-diagnostic-with-its-sampling-limits}

```python
from math import isclose
from fuzzyroutines import (
    ContinuousUniverse, IntegrationDomain, LinguisticScale, LinguisticTerm,
    ScalarFuzzySet, ScaleDiagnosticPoint, ScaleDiagnosticsPolicy,
    ScaleDiagnosticsResult, TermMembership, Triangle,
)

universe = ContinuousUniverse(0, 2, leftClosed=True, rightClosed=True)
first = LinguisticTerm("Preferred A", ScalarFuzzySet(universe, Triangle(0, 1, 2)))
second = LinguisticTerm("Preferred B", ScalarFuzzySet(universe, Triangle(0, 1, 2)))
scale = LinguisticScale((first, second))
report = scale.Diagnose(IntegrationDomain(0, 2), ScaleDiagnosticsPolicy(sampleCount=3))
point = ScaleDiagnosticPoint(1, (TermMembership(first, 1), TermMembership(second, 1)), 0)
assert point == report.points[1]
assert point.maximumMembership == 1 and point.membershipSum == 2
assert point.activeTerms == (first, second) and point.isOverlap and not point.isGap
assert point.partitionError == 1
copy = ScaleDiagnosticsResult(report.analysisDomain, report.policy, report.points)
assert copy == report
assert tuple(point.coordinate for point in copy.gapPoints) == (0, 2)
assert tuple(point.coordinate for point in copy.overlapPoints) == (1,)
assert isclose(copy.gapFraction, 2 / 3) and isclose(copy.overlapFraction, 1 / 3)
assert copy.minimumCoverage == 0 and copy.maximumCoverage == 1
assert isclose(copy.meanCoverage, 1 / 3) and copy.maximumActiveTermCount == 2
assert copy.meanPartitionError == copy.maximumPartitionError == 1
assert not copy.isPartitionWithinTolerance
print(copy.gapFraction, copy.overlapFraction, copy.meanCoverage)
```


有意重复的三角形使中间观测成为重叠点，两个底点成为空缺。覆盖值是该坐标处的最大隶属度，与全部隶属度之和不同。分解误差是该和与一之差的绝对值。比例和平均值统计的是三个观测，而不是区间长度或连续积分。词项仅在严格高于策略的 `membershipThreshold` 时活跃；相等时不活跃。这张表不能证明全局覆盖或单位分解。
