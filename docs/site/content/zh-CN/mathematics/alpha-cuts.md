<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# α 截集契约 {#alpha-cut-contract}

## 定义与边界约定 {#definition-and-boundary-convention}

对于论域 $X$ 上的标量模糊集 $A$，FuzzyRoutines 将弱 α 截集定义为

$$
A_\alpha = \{x \in X \mid \mu_A(x) \ge \alpha\},
\qquad \alpha \in [0, 1].
$$

比较直接采用 `>=`。隶属度等于阈值的坐标属于截集。
API 不会静默替换为强截集 $\{x \mid \mu_A(x) > \alpha\}$，也不应用数值容差。

端点语义直接由定义得到：

- $A_0 = X$，因为每个有效隶属度均位于 $[0, 1]$；
- $A_1 = \{x \in X \mid \mu_A(x) = 1\}$，即 $A$ 的核。

对于任意 $0 \le \alpha \le \beta \le 1$，截集具有嵌套关系：

$$
A_\beta \subseteq A_\alpha.
$$

## 精确离散操作 {#exact-discrete-operation}

`AlphaCut(fuzzySet, alpha)` 穷举计算 `DiscreteUniverse` 的每个坐标，
并返回 `DiscreteRegion`。因此，结果是相对于声明的有限论域的精确截集。

```python
from fuzzyroutines import AlphaCut, DiscreteUniverse, ScalarFuzzySet

universe = DiscreteUniverse((0.0, 0.5, 1.0))
fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)

assert AlphaCut(fuzzySet, 0.5).points == (0.5, 1.0)
assert AlphaCut(fuzzySet, 0.0).points == universe.points
assert AlphaCut(fuzzySet, 1.0).points == (1.0,)
```

此操作通过 `ScalarFuzzySet.Membership` 求值，
因此非有限、非实数或超出范围的隶属度会导致明确失败。

## 明确采用采样的连续操作 {#explicitly-sampled-continuous-operation}

`ContinuousUniverse` 上的任意 Python 可调用对象通常没有通用的解析逆函数。
有限扫描不能证明其连续 α 截集。
因此，`AlphaCut` 拒绝连续模糊集，不会将采样点当作精确几何。

`SampleAlphaCut(fuzzySet, alpha, analysisDomain, sampleCount)` 是显式数值替代方法。
它在包含于集合论域内的 `IntegrationDomain` 上计算均匀有限网格，
并返回 `SampledAlphaCut`。结果记录：

- `alpha` 和弱条件 `>= alpha` 的筛选规则；
- `analysisDomain`、`sampleCount` 及全部求值坐标 `coordinates`；
- `grades` 中每个经过验证的隶属度；
- 以 `DiscreteRegion` 表示的所选 `cutSamples`；
- `method == "uniform-grid"` 和 `isExact == False`。

```python
from fuzzyroutines import (
    ContinuousUniverse,
    IntegrationDomain,
    SampleAlphaCut,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
sampledCut = SampleAlphaCut(
    fuzzySet,
    0.5,
    IntegrationDomain(0.0, 1.0),
    sampleCount=5,
)

assert sampledCut.cutSamples.points == (0.5, 0.75, 1.0)
assert sampledCut.isExact is False
```

当 `alpha=0` 时，`cutSamples` 包含整个声明网格，并不展开为整个连续论域。
当 `alpha=1` 时，它仅包含隶属度恰好为一的采样坐标，不能证明完整的连续核。
当各截集使用相同模糊集、分析域和网格分辨率时，保证嵌套不变量成立。

## 参考文献 {#references}

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
