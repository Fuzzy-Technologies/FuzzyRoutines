<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回离散标量模糊集的精确弱 α-截集。

返回区域包含所有满足 `fuzzySet.Membership(x) >= alpha` 的已声明坐标 `x`。该操作不接受连续论域：当前模型没有为任意隶属函数可调用对象提供解析逆函数或可穷举的有限表示。

Args:
    fuzzySet: 定义在离散论域上的标量模糊集。
    alpha: 用于弱截集的隶属度阈值，取值范围为 $[0, 1]$。

Returns:
    包含所有符合条件坐标的有序离散区域。

Raises:
    TypeError: 参数类型不符合离散约定。
    ValueError: `alpha` 不是 $[0, 1]$ 内的有限值。
