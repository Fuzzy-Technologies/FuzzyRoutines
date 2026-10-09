<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

计算 `x` 处高斯形指数函数的值。

Args:
    x: 有限的内置 `int` 或 `float` 坐标；不接受 `bool`。

Returns:
    $[0, 1]$ 内可表示的隶属度。数学上此函数为正，
    但足够远的有限输入可能下溢为精确的零。

Raises:
    ValueError: `x` 不是受支持的有限内置数值。
