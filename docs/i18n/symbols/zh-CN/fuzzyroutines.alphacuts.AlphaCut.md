<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回离散标量模糊集的精确弱 α-截集。

返回区域包含所有满足 `fuzzySet.Membership(x) >= alpha` 的已声明坐标 `x`。连续论域会明确拒绝，因为在当前模型中，任意隶属度可调用对象没有解析逆函数或有限的穷尽表示。

Args:
    fuzzySet: 定义在离散论域上的标量模糊集。
    alpha: $[0, 1]$ 内的弱隶属度阈值。

Returns:
    包含所有符合条件坐标的有序离散区域。

Raises:
    TypeError: 参数类型不符合离散约定。
    ValueError: `alpha` 不是 $[0, 1]$ 内的有限值。
