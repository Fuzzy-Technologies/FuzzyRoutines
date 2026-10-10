<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回有限坐标是否属于任一分量。

Args:
    coordinate: 要检验的有限实数坐标。

Returns:
    至少一个分量包含该坐标时返回 `True`。

Raises:
    TypeError: 区域非空且坐标不是实数标量。
    ValueError: 区域非空且坐标不是有限值。
