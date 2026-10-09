<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 模糊集相等与包含 {#fuzzy-set-equality-and-inclusion}

- 状态：任务 #73 的可执行契约
- 公共模块：`fuzzyroutines.relations`

## 数学关系 {#mathematical-relations}

对于同一论域 `X` 上的模糊集 `A` 和 `B`，逐点相等与包含定义为

```text
A = B  iff  for every x in X: mu_A(x) = mu_B(x)
A <= B iff  for every x in X: mu_A(x) <= mu_B(x)
```

公共 API 绝不比较隶属函数对象的身份。因此，两个不同的 Python 可调用对象
可以表示相同的隶属度行为。两种关系都要求在计算任何隶属度之前确认论域精确相等。
`ScalarFuzzySet` 的 Python 对象相等仍基于身份，不是数学关系；
调用者必须使用显式关系函数。

## 穷举与采样范围 {#exhaustive-and-sampled-scope}

`DiscreteUniverse` 有限，因此 `EqualOnDomain` 和 `IncludedOnDomain`
会计算每个声明点。调用者不能提供部分比较域，却意外地把结果标记为整个论域上的相等。

通常，有限次求值无法证明 `ContinuousUniverse` 上任意 Python 可调用对象
与另一个对象全局相等。因此，连续关系要求显式 `ComparisonDomain`，
包含论域内有限且有序的采样点。布尔结果仅对这些声明点有效，
不是点间函数相等或包含的证明。

此边界是有意设定的。对已知隶属函数族进行解析关系证明需要单独的符号表示与契约。

## 精确模式与容差模式 {#exact-and-tolerance-modes}

每个关系都要求 `ComparisonPolicy`：

- `ComparisonPolicy("exact")` 使用精确的隶属度数值相等及精确逐点序关系；
- `ComparisonPolicy("tolerance", absoluteTolerance=..., relativeTolerance=...)`
  使用 `math.isclose` 判断相等，仅当两个隶属度在这些显式容差下足够接近时，
  才允许包含关系的偏差。

容差模式要求两个容差字段，且至少一个必须为正。精确模式拒绝容差参数。
不存在库级或隐式 epsilon。

基于容差的接近关系一般不满足传递性，不可作为哈希、规范化表示或身份判断的等价关系。

## 示例 {#examples}

穷举离散比较：

```python
from fuzzyroutines import (
    ComparisonPolicy,
    DiscreteUniverse,
    EqualOnDomain,
    IncludedOnDomain,
    ScalarFuzzySet,
)

universe = DiscreteUniverse((0.0, 0.5, 1.0))
leftSet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
rightSet = ScalarFuzzySet(universe, lambda coordinate: coordinate**1)
policy = ComparisonPolicy("exact")

assert EqualOnDomain(leftSet, rightSet, policy)
assert IncludedOnDomain(leftSet, rightSet, policy)
```

显式连续采样比较：

```python
from fuzzyroutines import ComparisonDomain, ContinuousUniverse

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
leftSet = ScalarFuzzySet(universe, lambda coordinate: coordinate * coordinate)
rightSet = ScalarFuzzySet(universe, lambda coordinate: coordinate**2)
samplePoints = ComparisonDomain((0.0, 0.25, 0.5, 0.75, 1.0))

assert EqualOnDomain(leftSet, rightSet, policy, samplePoints)
```

## 已验证的性质 {#verified-properties}

可执行测试套件覆盖：

- 穷举离散相等与包含；
- 不同身份的可调用表示之间的相等；
- 自反性和精确反对称性；
- 显式绝对及相对容差行为；
- 连续比较域的必需性；
- 拒绝部分离散域；
- 拒绝不兼容论域及无效采样点。

## 参考文献 {#references}

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- G. J. Klir and B. Yuan, *Fuzzy Sets and Fuzzy Logic: Theory and
  Applications*, Prentice Hall, 1995. ISBN 978-0-13-101171-7.
