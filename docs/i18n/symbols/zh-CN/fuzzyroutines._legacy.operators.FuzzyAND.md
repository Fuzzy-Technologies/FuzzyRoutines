<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回两个隶属度的最小值。

Args:
    aNumber: 左侧隶属度，内置 `int` 或 `float` 类型，位于 $[0, 1]$。
    bNumber: 右侧隶属度，内置 `int` 或 `float` 类型，位于 $[0, 1]$。

Returns:
    `min(aNumber, bNumber)`。

Raises:
    ValueError: 操作数为 `bool` 或其他不受支持的类型、不是有限值，或不在 $[0, 1]$ 内。
