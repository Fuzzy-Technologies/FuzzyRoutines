<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

计算 `x` 处数值稳定的 Logistic 函数的值。

Args:
    x: 有限的内置 `int` 或 `float` 坐标；不接受 `bool`。

Returns:
    $[0, 1]$ 内可表示的隶属度。对于绝对值足够大的有限输入，
    浮点下溢和舍入可能产生任一端点值。

Raises:
    ValueError: `x` 不是受支持的有限内置数值。
