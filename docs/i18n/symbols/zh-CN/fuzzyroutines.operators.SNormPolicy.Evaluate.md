<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

对两个隶属度计算已配置的 S-范数。

Args:
    leftGrade: $[0, 1]$ 内的左隶属度。
    rightGrade: $[0, 1]$ 内的右隶属度。

Returns:
    已配置函数族的析取结果。

Raises:
    TypeError: 操作数不是实数标量。
    ValueError: 操作数非有限或超出 $[0, 1]$。
