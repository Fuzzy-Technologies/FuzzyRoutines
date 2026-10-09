<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回有限标量坐标是否属于论域。

Args:
    coordinate: 要检查的有限实数坐标。

Returns:
    当且仅当坐标满足两个端点规则时返回 `True`。

Raises:
    TypeError: 坐标不是实数标量。
    ValueError: 坐标不是有限值。
