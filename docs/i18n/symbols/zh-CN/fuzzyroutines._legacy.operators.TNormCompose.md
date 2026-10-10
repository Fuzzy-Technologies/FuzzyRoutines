<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

从左向右将同一个 t 范数依次应用于一个或多个隶属度。

Args:
    *fuzzyNumbers: $[0, 1]$ 内的内置 `int` 或 `float` 隶属度；不接受 `bool`。
    normType: `"logic"`、`"algebraic"`、`"boundary"` 或 `"drastic"` 之一。

Returns:
    按左结合顺序计算全部操作数的合取。

Raises:
    ValueError: 未提供操作数、某个操作数无效，或函数族未知。
