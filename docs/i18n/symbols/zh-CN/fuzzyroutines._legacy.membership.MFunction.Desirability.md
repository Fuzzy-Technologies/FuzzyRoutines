<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

计算 `y` 处 Harrington 期望度函数的值。

Args:
    y: 有限的内置 `int` 或 `float` 期望度坐标；不接受 `bool`。

Returns:
    $[0, 1]$ 内可表示的隶属度。足够小的负值会确定性地下溢为零，
    足够大的正值会舍入为一。

Raises:
    ValueError: `y` 不是受支持的有限内置数值。
