<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 模糊集高度与归一化 {#fuzzy-set-height-and-normalization}

- 状态：任务 #76 的可执行契约
- 相关 Feature：#25
- 相关 ADR：[ADR-0002](../../../../adr/0002-universe-support-semantics.md)
- 公共模块：`fuzzyroutines.fuzzysets`

## 数学契约 {#mathematical-contract}

对于标量模糊集 `A = (X, mu_A)`，高度和正规性定义为

```text
height(A)   = sup({mu_A(x) | x in X})
isNormal(A) = height(A) = 1
```

当 `height(A) > 0` 时，归一化在同一论域上构造新集合：

```text
mu_Normalize(A)(x) = mu_A(x) / height(A)
```

结果的精确高度为一，因为上确界乘以了正常数 `1 / height(A)`。
高度为零时，此商没有定义；`Normalize` 抛出 `ValueError`，
不会原样返回空集或人为创造单位隶属度。

## 精确性边界 {#exactness-boundary}

`Height` 遵循现有属性契约，不另行实现一套隶属函数族公式：

- `DiscreteUniverse` 有限，对每个声明坐标穷举求值；
- 当集合使用现代解析 `MembershipFunction` 或受支持的历史 `MFunction` 求值器时，
  支持 `ContinuousUniverse`；高度来自 `DeriveProperties` 及其精确函数族几何；
- 归一化结果保留内部的精确高度为一的依据；
- 任意连续可调用对象会被拒绝，因为有限次求值无法证明其全局上确界。

`SampleProperties(...).heightEstimate` 仍是一个有限 `IntegrationDomain` 上的近似观测。
它有意不被接受为精确归一化的依据。增加采样点数可以改进估计，
但无法证明一般连续函数的上确界，在无界论域上尤其如此。

## 数值精度 {#precision}

`Height` 以标量数值表示返回契约规定的精确值。
`IsNormal(fuzzySet, tolerance=1e-12)` 使用零相对容差和调用者可见的绝对容差将此值与一比较。
布尔、负数及非有限容差会被拒绝。容差仅影响正规性谓词，
绝不会将很小的正高度当作零，也不会改变归一化的除数。

隶属函数求值器仍验证每个返回值是否位于 `[0, 1]`。
归一化不会截断浮点计算造成的越界。一般自定义连续函数会被拒绝；
受支持的解析及离散定义会保存快照，而不保留可变源对象的语义。

## 不可变性与求值范围 {#immutability-and-evaluation-scope}

`Normalize` 始终返回独立的冻结 `ScalarFuzzySet`，绝不修改源对象。
对于离散论域，源隶属度按照论域顺序各求值一次，归一化结果使用此完整不可变快照。
对于连续解析来源，在归一化时捕获规范函数族标识符和不可变参数元组。
惰性求值使用共享解析公式核心与冻结快照，再按精确推导的高度缩放。
因此，之后修改源 `MFunction.parameters` 不会破坏归一化结果高度为一的依据。

正规性使用上确界，不要求存在核中的点。
因此，即使没有有限坐标达到隶属度一，连续模糊集仍可能是正规的。

## 示例 {#example}

```python
from fuzzyroutines import (
    ContinuousUniverse,
    Height,
    IsNormal,
    Normalize,
    ScalarFuzzySet,
)
from fuzzyroutines.FuzzyRoutines import MFunction

membershipFunction = MFunction("logistic", a=2.0, b=0.0)
universe = ContinuousUniverse(-1.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)

assert Height(fuzzySet) < 1.0
normalizedSet = Normalize(fuzzySet)
assert IsNormal(normalizedSet)
assert normalizedSet.universe == fuzzySet.universe
```

## 参考文献 {#references}

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- G. J. Klir and B. Yuan, *Fuzzy Sets and Fuzzy Logic: Theory and
  Applications*, Prentice Hall, 1995, ISBN 978-0-13-101171-7.
  <https://books.google.com/books?id=AOhQAAAAMAAJ>
