<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

使用一个显式的已认可否定策略返回新模糊集。

Args:
    fuzzySet: 源标量模糊集。
    negationPolicy: 显式补运算语义。

Returns:
    保持原论域、采用惰性求值的不可变集合。

Raises:
    TypeError: 任一参数的类型不符合约定。
