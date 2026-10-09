<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

计算 `x` 处具有右侧尾部的双曲隶属函数的值。

Args:
    x: 有限的内置 `int` 或 `float` 坐标；不接受 `bool`。

Returns:
    $[0, 1]$ 内的隶属度。

Raises:
    ValueError: `x` 不是受支持的有限内置数值。
    OverflowError: 有限输入产生无法表示的幂运算中间结果。
