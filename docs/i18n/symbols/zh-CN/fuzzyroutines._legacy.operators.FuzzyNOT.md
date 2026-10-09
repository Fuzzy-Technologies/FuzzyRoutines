<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

计算历史参数化模糊否定。

当 `alpha=0.5` 时，结果为标准补运算 $1 - fuzzyNumber$。

Args:
    fuzzyNumber: 位于 $[0, 1]$ 内的内置 `int` 或 `float` 隶属度；不接受 `bool`。
    alpha: 位于 $(0, 1)$ 内的内置 `int` 或 `float` 不动点；不接受 `bool`。

Returns:
    补集的隶属度。

Raises:
    ValueError: 任一参数的类型不受支持、不是有限值，或超出其允许范围。
