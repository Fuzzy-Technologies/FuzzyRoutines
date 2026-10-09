<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回有限标量坐标是否已在论域中声明。

Args:
    coordinate: 要检查的有限实数坐标。

Returns:
    `coordinate` 是某个已声明点时返回 `True`。

Raises:
    TypeError: 坐标不是实数标量。
    ValueError: 坐标不是有限值。
