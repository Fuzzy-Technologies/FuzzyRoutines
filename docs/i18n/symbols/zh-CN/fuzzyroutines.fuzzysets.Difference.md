<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

根据显式策略返回有向模糊集差。

隶属度定义为 $T(\mu_A(x), N(\mu_B(x)))$。

Args:
    leftSet: 被减的标量模糊集 $A$。
    rightSet: 相同论域上的减去集合 $B$。
    tNormPolicy: 显式合取语义 $T$。
    negationPolicy: 显式补运算语义 $N$。

Returns:
    共享论域上采用惰性求值的不可变有向差。

Raises:
    TypeError: 参数类型不符合约定。
    ValueError: 操作数的论域不同。
