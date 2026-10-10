<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回两个隶属度是否按本策略相等。

Args:
    leftGrade: $[0, 1]$ 内的左隶属度。
    rightGrade: $[0, 1]$ 内的右隶属度。

Returns:
    根据 `mode` 使用精确相等或 `math.isclose`。

Raises:
    TypeError: 任一隶属度不是实数标量。
    ValueError: 任一隶属度非有限或超出 $[0, 1]$。
