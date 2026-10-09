<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 显式模糊集操作 {#explicit-fuzzy-set-operations}

- 状态：任务 #71、#72 和 #74 的可执行契约
- 相关 ADR：[ADR-0004](../../../../adr/0004-operator-and-negation-contracts.md)
  和 [ADR-0008](../../../../adr/0008-fuzzy-set-difference-semantics.md)
- 公共模块：`fuzzyroutines.fuzzysets`

## 集合表示 {#set-representation}

`ScalarFuzzySet` 是有序对

```text
A = (X, mu_A)
mu_A: X -> [0, 1]
```

其中 `X` 是显式的 `ContinuousUniverse` 或 `DiscreteUniverse`。
隶属度求值拒绝 `X` 之外的坐标，并拒绝布尔、非有限或超出范围的隶属度，不进行强制转换。

值对象的字段不可变。操作在同一论域上构造新的隶属函数求值器，不修改任一操作数。
提供自定义可调用对象的调用者仍有责任保证它可重入，并且不受外部可变语义影响。

## 论域兼容性 {#universe-compatibility}

二元操作要求论域精确相等，包括连续端点值、端点闭合性、表示类型和离散点。
初始 API 不为不同论域推断并集、交集、重采样网格或坐标转换。
此类协调应是具有独立策略的另一项数学操作。

## 补集 {#complement}

给定显式否定 `N`，补集逐点计算：

```text
mu_complement(A)(x) = N(mu_A(x))
```

`NegationPolicy` 仅支持 ADR-0004 接受的函数族：

- `standard`：`N(x) = 1 - x`，不带参数；
- `parametric`：历史分段线性强否定，显式 `alpha` 位于 `(0, 1)`；
- `parabolic`：已接受的解析分支，显式 `alpha` 位于 `[1/4, 3/4]`。

没有默认或进程级否定设置。即使是标准补运算，也必须通过 `NegationPolicy("standard")` 请求。

## 交集与并集 {#intersection-and-union}

给定显式 t 范数 `T` 和 s 范数 `S`：

```text
mu_intersection(A, B)(x) = T(mu_A(x), mu_B(x))
mu_union(A, B)(x)        = S(mu_A(x), mu_B(x))
```

`TNormPolicy` 和 `SNormPolicy` 接受 `logic`、`algebraic`、`boundary` 和 `drastic`。
公式与 ADR-0004 记录的公式完全一致。
`Intersection` 和 `Union` 都没有隐藏的默认函数族。

## 有向差集 {#directed-difference}

差集是与右操作数的显式所选补集相交：

```text
mu_Difference(A, B)(x) = T(mu_A(x), N(mu_B(x)))
```

因此，`Difference` 同时要求 `TNormPolicy` 和 `NegationPolicy`。
操作数的论域必须精确相等，结果保留该论域。此操作有方向性，不修改任一操作数。

对于清晰的二值隶属度，标准否定与逻辑 t 范数可还原经典差集。
一般模糊隶属度保留所选算子的语义；特别是，不保证 `Difference(A, A)` 为空。
ADR-0008 未定义对称差集，因为组合两个有向差集还需要 s 范数，
而且在任意算子策略下不能保留所有经典定律。

## 示例 {#example}

```python
from fuzzyroutines import (
    Complement,
    ContinuousUniverse,
    Difference,
    Intersection,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
    Union,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
increasingSet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
decreasingSet = Complement(increasingSet, NegationPolicy("standard"))

overlap = Intersection(increasingSet, decreasingSet, TNormPolicy("logic"))
envelope = Union(increasingSet, decreasingSet, SNormPolicy("logic"))
directedDifference = Difference(
    increasingSet,
    decreasingSet,
    TNormPolicy("logic"),
    NegationPolicy("standard"),
)
```

## 已验证的定律 {#verified-laws}

可执行性质测试覆盖全部四对已接受的对偶函数族：

- 在 `[0, 1]` 内封闭；
- 交换律；
- 结合律；
- t 范数单位元 `T(x, 1) = x`；
- s 范数单位元 `S(x, 0) = x`；
- 标准否定下的两条德摩根定律；
- 有向差集等价于 `T(mu_A(x), N(mu_B(x)))`；
- 与清晰集的兼容性、方向性，以及显式拒绝不兼容论域或缺少策略的调用。

现代标量策略还会在确定性参考网格上与受保护的历史标量函数进行核对。
相等与包含使用[模糊集相等与包含](../../../../mathematics/fuzzy-set-relations.md)
所述的独立契约，在不受支持的情况下明确失败；
算子参考网格不会静默复用为比较域。

## 参考文献 {#references}

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- E. P. Klement, R. Mesiar, and E. Pap, *Triangular Norms*, Springer, 2000.
  <https://doi.org/10.1007/978-94-015-9540-7>
