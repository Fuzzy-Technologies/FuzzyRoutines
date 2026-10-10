<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

按一个显式 S-范数族返回模糊集并。

Args:
    leftSet: 左标量模糊集。
    rightSet: 具有完全相同论域的右标量模糊集。
    sNormPolicy: 显式析取语义。

Returns:
    共享论域上采用惰性求值的不可变并集。

Raises:
    TypeError: 参数类型不符合约定。
    ValueError: 操作数的论域不同。
