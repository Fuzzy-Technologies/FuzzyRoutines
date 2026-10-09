<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 实用 API 示例 {#practical-api-recipes}

[完整场景](index.md)解释完整计算过程。这里的较小示例涵盖域验证、采样性质、其他运算选择、有限比较和错误处理。每个 Python 代码块均可独立运行，并在 CI 中针对已安装的 wheel 和 sdist 产物执行。

## 积分前验证域 {#validate-a-domain-before-integration}

```python
from fuzzyroutines import ContinuousUniverse, DiscreteUniverse, IntegrationDomain

universe = ContinuousUniverse(0, 10, leftClosed=True, rightClosed=True)
domain = IntegrationDomain.FromLegacyInterval((2, 8)).ValidateWithin(universe)
assert universe.isBounded and universe.Contains(0)
assert domain.Contains(2) and domain.ToLegacyInterval() == (2, 8)
discrete = DiscreteUniverse((1, 3, 5))
assert discrete.Contains(3) and not discrete.Contains(2)
print(domain.ToLegacyInterval(), discrete.points)
```


积分窗口是有限闭区间，不是数学上的支集。论域可以无界或具有开端点；请求的积分窗口必须遵守这些端点限制。

## 读取精确与采样性质 {#read-exact-and-sampled-properties}

```python
from fuzzyroutines import (
    ContinuousInterval, ContinuousRegion, ContinuousUniverse, DeriveProperties,
    DiscreteRegion, IntegrationDomain, IsNormal, SampleProperties,
    ScalarFuzzySet, Triangle,
)

model = Triangle(0, 2, 4)
universe = ContinuousUniverse(0, 4, leftClosed=True, rightClosed=True)
properties = DeriveProperties(model, universe)
sampled = SampleProperties(model, IntegrationDomain(0, 4), sampleCount=5)
assert properties.isExact and properties.height == 1
assert properties.core.Contains(2) and not properties.positiveSupport.Contains(0)
assert not sampled.isExact and sampled.heightEstimate == 1
assert sampled.coreSamples.points == (2,)
assert IsNormal(ScalarFuzzySet(universe, model))
interval = ContinuousInterval(1, 3, leftClosed=True, rightClosed=False)
region = ContinuousRegion((interval,))
assert region.Contains(1) and not region.Contains(3) and not region.isEmpty
assert not interval.isSingleton and not DiscreteRegion((1, 3)).isEmpty
print(properties.height, sampled.coordinates)
```


对于内置解析函数族，`DeriveProperties` 计算限制在论域内的精确几何性质。`SampleProperties` 报告指定网格上观察到的支集、核、边界和高度估计。本例恰好采到峰值，因此估计为一；其他模型若漏掉窄峰，就可能低估高度。一般连续模型的精确高度不会从采样推断。`IsNormal` 使用精确高度和显式容差，默认容差为 $10^{-12}$。

## 有意识地选择标量运算族 {#choose-scalar-operator-families-deliberately}

```python
from math import isclose
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy

expectedAnd = {"logic": 0.4, "algebraic": 0.28, "boundary": 0.1, "drastic": 0}
expectedOr = {"logic": 0.7, "algebraic": 0.82, "boundary": 1, "drastic": 1}
for family in expectedAnd:
    assert isclose(TNormPolicy(family).Evaluate(0.4, 0.7), expectedAnd[family], abs_tol=1e-12)
    assert isclose(SNormPolicy(family).Evaluate(0.4, 0.7), expectedOr[family], abs_tol=1e-12)
assert NegationPolicy("standard").Evaluate(0.4) == 0.6
assert NegationPolicy("parametric", alpha=0.5).Evaluate(0.5) == 0.5
assert NegationPolicy("parabolic", alpha=0.5).Evaluate(0.5) == 0.5
print(expectedAnd, expectedOr)
```


参数化否定要求 $0<\alpha<1$；抛物线否定要求 $1/4\leq\alpha\leq3/4$。这里的 α 是否定参数，不是 α-截集阈值。有界与剧烈策略是显式备选；端点处的突变行为可能影响模型。

## 在显式坐标处比较连续模型 {#compare-continuous-models-at-explicit-coordinates}

```python
from fuzzyroutines import (
    ComparisonDomain, ComparisonPolicy, ContinuousUniverse,
    EqualOnDomain, IncludedOnDomain, ScalarFuzzySet, Triangle,
)

universe = ContinuousUniverse(0, 4, leftClosed=True, rightClosed=True)
left = ScalarFuzzySet(universe, Triangle(0, 2, 4))
right = ScalarFuzzySet(universe, Triangle(0, 2, 4))
coordinates = ComparisonDomain((0, 1, 2, 3, 4)).ValidateWithin(universe)
policy = ComparisonPolicy("tolerance", absoluteTolerance=1e-12, relativeTolerance=1e-10)
assert policy.Equal(0.5, 0.5 + 1e-13)
assert policy.Included(0.4, 0.5)
assert EqualOnDomain(left, right, policy, coordinates)
assert IncludedOnDomain(left, right, policy, coordinates)
print(coordinates.points)
```


结果只证明五个声明的观测处的关系。即使独立解析论证能说明这两个特定定义相同，该结果本身也不是全局连续等价性的证明。

## 处理数学上未定义的结果 {#handle-a-mathematically-undefined-result}

```python
from fuzzyroutines import (
    Centroid, CentroidPolicy, ContinuousUniverse, IntegrationDomain,
    MembershipScalar, ScalarFuzzySet,
)
from fuzzyroutines.exceptions import UndefinedResultError


def ZeroGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return zero area on every allowed coordinate."""

    return 0


empty = ScalarFuzzySet(
    ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True), ZeroGrade,
)
try:
    Centroid(empty, IntegrationDomain(0, 1), CentroidPolicy(maximumDepth=20))
except UndefinedResultError:
    print("No centroid: the membership area is zero")
else:
    raise AssertionError("zero-area membership unexpectedly had a centroid")
```


应选择符合领域语义的后备行为，或继续传播此错误。静默返回零会凭空指定一个代表性坐标。无效类型、参数和域具有各自的异常类别；自适应细化耗尽使用 `CentroidConvergenceError`。应捕获应用确实能够处理的具体类别，而不是抑制全部错误。
