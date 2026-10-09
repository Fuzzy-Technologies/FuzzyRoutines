<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

计算历史函数族注册表中的二元 s 范数。

Args:
    aFuzzyNumber: 左侧隶属度，内置 `int` 或 `float` 类型，位于 $[0, 1]$。
    bFuzzyNumber: 右侧隶属度，内置 `int` 或 `float` 类型，位于 $[0, 1]$。
    normType: `"logic"`、`"algebraic"`、`"boundary"` 或 `"drastic"` 之一。

Returns:
    按所选函数族得到的两个隶属度的析取。

Raises:
    ValueError: 操作数不是 $[0, 1]$ 内受支持的有限内置数值，或函数族未知。
