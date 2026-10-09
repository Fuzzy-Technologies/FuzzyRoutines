<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

在穷尽域或显式有限域上比较隶属度是否相等。

对于离散论域，全部声明点构成穷尽检查，必须省略 `comparisonDomain`。对于连续论域，结果仅描述显式给出的采样点，不证明全局函数相等。

Args:
    leftSet: 左标量模糊集。
    rightSet: 具有完全相同论域的右标量模糊集。
    comparisonPolicy: 精确或容差隶属度比较策略。
    comparisonDomain: 连续论域必需的有限观测点；离散论域应省略。

Returns:
    所有已求值的隶属度对按策略比较相等时返回 `True`。

Raises:
    TypeError: 参数类型不符合约定。
    ValueError: 论域不同或比较域选择无效。
