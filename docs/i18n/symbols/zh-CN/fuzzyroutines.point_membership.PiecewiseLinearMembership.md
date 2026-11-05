<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

在严格递增的节点之间作线性插值的隶属函数。

在每个节点处原样返回保存的隶属度。对相邻节点 $(a, g_a)$ 和 $(b, g_b)$
以及它们之间的坐标 $x$，隶属度为 $(1-t)g_a+tg_b$，其中 $t=(x-a)/(b-a)$。
插值涉及的数值都是整数或有理数类型时，结果为 `Fraction`；其他插值结果为浮点数。
不允许重复节点，也不能表示内部跳变。零延拓会在隶属度非零的端点处产生跳变。

Attributes:
    knots: 由至少两个 `(坐标, 隶属度)` 二元组组成的元组。坐标有限且严格递增；
        隶属度有限且位于 $[0, 1]$。不接受布尔值。
    boundary: 严格位于节点区间之外时的行为：`"zero"` 返回零，
        `"clamp"` 返回最近端点的隶属度，`"error"` 引发 `InvalidDomainError`。
        默认值为 `"error"`。
