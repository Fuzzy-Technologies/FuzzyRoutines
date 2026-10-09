<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回方程 $2a-x-y=(2a-1)(y-x)^2$ 的有效分支。

Args:
    fuzzyNumber: 位于 $[0, 1]$ 内的内置 `int` 或 `float` 隶属度；不接受 `bool`。
    alpha: 位于 $[1/4, 3/4]$ 内的内置 `int` 或 `float` 不动点；不接受 `bool`。
    epsilon: 已弃用的兼容参数；解析解有意忽略此参数。

Returns:
    `fuzzyNumber` 的抛物型补运算结果。

Raises:
    ValueError: `fuzzyNumber` 或 `alpha` 的类型不受支持、不是有限值，或超出允许范围。
