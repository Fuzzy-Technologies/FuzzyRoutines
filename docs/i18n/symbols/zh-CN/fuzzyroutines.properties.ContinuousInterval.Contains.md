<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回有限坐标是否属于此区间。

Args:
    coordinate: 要检验的有限实数坐标。

Returns:
    当且仅当端点规则允许该坐标时返回 `True`。

Raises:
    TypeError: 坐标不是实数标量。
    ValueError: 坐标不是有限值。
