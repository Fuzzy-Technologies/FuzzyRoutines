<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 自定义质量模型 {#a-custom-quality-model}

**问题：**领域专用的标量函数能否在不继承任何类的情况下，参与积分和有限论域上的归一化？

```python
from math import isclose
from fuzzyroutines import (
    Centroid, ComparisonPolicy, ContinuousUniverse, DiscreteUniverse,
    EqualOnDomain, Height, IncludedOnDomain, IntegrationDomain,
    MembershipCallable, MembershipScalar, Normalize, ScalarFuzzySet,
)


def RisingQuality(coordinate: MembershipScalar) -> MembershipScalar:
    """Map a declared score in [0, 100] to its linear membership grade."""

    return coordinate / 100


callback: MembershipCallable = RisingQuality
continuous = ScalarFuzzySet(
    ContinuousUniverse(0, 100, leftClosed=True, rightClosed=True), callback,
)
centroid = Centroid(continuous, IntegrationDomain(0, 100))
assert isclose(centroid, 200 / 3, abs_tol=1e-9)
discrete = ScalarFuzzySet(DiscreteUniverse((0, 25, 50)), RisingQuality)
normalized = Normalize(discrete)
assert Height(discrete) == 0.5 and Height(normalized) == 1
assert tuple(normalized.Membership(coordinate) for coordinate in discrete.universe.points) == (0, 0.5, 1)
policy = ComparisonPolicy("exact")
assert IncludedOnDomain(discrete, normalized, policy)
assert not EqualOnDomain(discrete, normalized, policy)
print(centroid, Height(discrete), Height(normalized))
```


可调用对象的约定是：接受一个有限、非布尔的实数坐标，返回 $[0,1]$ 内的有限隶属度。`MembershipScalar` 表达更广的受支持标量输入类型。构造时检查是否可调用；求值时检查坐标和返回的隶属度。应保持各次调用间的隶属度一致；库不会为任意函数所捕获的可变状态创建快照。

函数 $x/100$ 在 $[0,100]$ 上的面积为 50，一阶矩为 $10000/3$，因此质心为 $200/3\approx66.666667$，与自适应计算一致。内置解析几何机制无法证明任意可调用函数的精确连续高度或支集。采样可以描述观测，但不能提供这种证明。

[![三个声明的离散坐标上的原始与归一化隶属度](../../en/assets/figures/custom.svg)](../../en/assets/figures/custom.svg)

在离散论域 $\{0,25,50\}$ 上，穷尽求值可证明高度为 0.5。`Normalize` 将每个隶属度除以该高度并返回新集合，原集合保持不变。图中有意只绘制点，因为声明的论域并不包含中间坐标。

精确比较确立了**全部三个声明点**上的包含关系。连续模型的 `EqualOnDomain` 和 `IncludedOnDomain` 则要求显式有限 `ComparisonDomain`，它们只证明这些观测处的关系，而不是整个区间上的相等或包含。使用容差策略时，必须明确给出绝对和相对容差。

**项目用法：**将稳定的校准函数包装在声明的论域中，保留单位和验证假设，并对代表性案例验证独立积分。只有当把最大隶属度缩放到一符合应用语义时，才应进行归一化。

```bash
python -I examples/guide.py --scenario custom
```


继续阅读[隶属函数图集](membership-families.md)或[完整 API 参考](../api/index.md)。
