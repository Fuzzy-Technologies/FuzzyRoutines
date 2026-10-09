<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

对一个隶属度计算已配置的否定。

Args:
    grade: $[0, 1]$ 内的有限隶属度。

Returns:
    按本策略得到的补隶属度。

Raises:
    TypeError: `grade` 不是实数标量。
    ValueError: `grade` 非有限或超出 $[0, 1]$。
