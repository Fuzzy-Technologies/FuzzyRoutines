<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 由显式点定义隶属函数 {#membership-from-explicit-points}

一次校准给出了坐标 10、13 和 21 处的隶属度。如果模型只定义这三个坐标，
就使用离散隶属度表。如果需要在测量点之间沿直线确定隶属度，就使用分段线性隶属函数。

```python
from fuzzyroutines import ContinuousUniverse, ScalarFuzzySet
from fuzzyroutines.point_membership import (
    DiscreteMembershipTable,
    PiecewiseLinearMembership,
)

points = ((10, 0.25), (13, 0.75), (21, 0.5))
table = DiscreteMembershipTable(points)
curve = PiecewiseLinearMembership(points, boundary="zero")
discrete = ScalarFuzzySet(table.universe, table)
continuous = ScalarFuzzySet(ContinuousUniverse(), curve)

assert discrete.Membership(13) == continuous.Membership(13) == 0.75
assert continuous.Membership(11.5) == 0.5
assert continuous.Membership(17) == 0.625
assert continuous.Membership(22) == 0
```

表中没有坐标 17 的隶属度，因为 17 不在其论域中。曲线上 17 的隶属度是
0.625：它正好位于 13 和 21 中间，这两个坐标的隶属度分别为 0.75 和 0.5。
第一个区间宽 3 个单位，第二个宽 8 个单位；每段都使用自己的实际宽度。

## API 参考 {#api-reference}

`DiscreteMembershipTable(points)` 接受一个非空元组，其中每项都是
`(坐标, 隶属度)` 二元组。只读属性 `points` 和 `universe` 分别提供数据及
对应的 `DiscreteUniverse`。表在构造时验证并保存全部隶属度；将
`DiscreteUniverse` 与回调配合使用时，论域只声明坐标，隶属度由回调计算。
查询未声明的坐标会引发 `InvalidDomainError`。坐标按数值精确匹配，不使用容差。

`PiecewiseLinearMembership(knots, boundary="error")` 使用相同格式，至少需要两个节点。
`knots` 和 `boundary` 均为只读属性。在节点处返回保存的隶属度。对相邻节点
$(x_i,g_i)$ 和 $(x_{i+1},g_{i+1})$，令 $t=(x-x_i)/(x_{i+1}-x_i)$。
在它们之间的坐标 $x$ 处，隶属度为 $(1-t)g_i+tg_{i+1}$。
插值涉及的数值都是整数或有理数类型时，结果为 `Fraction`；涉及浮点值时，
结果为 Python float。

在节点闭区间之外：

- `"error"` 引发 `InvalidDomainError`（默认行为）。
- `"zero"` 返回 0。端点的隶属度非零时，该端点处会发生跳变。
- `"clamp"` 返回最近端点的隶属度。

区间内部不能表示跳变。尝试用重复坐标表示跳变会引发 `InvalidDomainError`。

两个可调用对象都接受一个位置参数 `MembershipScalar`。输入数据的坐标必须有限且
严格递增；隶属度必须有限且位于 $[0,1]$ 内。布尔值及其他非实数值会引发
`InvalidParameterTypeError`。非有限坐标、非有限或超出范围的隶属度以及未知的
边界策略字符串都会引发 `InvalidParameterError`。构造时不会排序或归一化。

分段线性函数的边界策略不会覆盖 `ScalarFuzzySet` 声明的论域。标量调用协议不会把
该曲线注册为可推导精确连续性质或可解析计算质心的函数。详见
[ADR-0024](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/adr/0024-point-membership-contracts.md)
和[解析隶属函数参考](membership.md)。

::: fuzzyroutines.point_membership
    options:
      members:
        - DiscreteMembershipTable
        - PiecewiseLinearMembership
