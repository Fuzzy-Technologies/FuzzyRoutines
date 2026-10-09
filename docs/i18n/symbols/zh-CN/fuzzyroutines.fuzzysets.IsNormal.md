<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回模糊集的精确高度是否在容差内等于一。

Args:
    fuzzySet: 具有可证明精确高度的标量模糊集。
    tolerance: 非负绝对比较容差。

Returns:
    精确高度与一的差是否在 `tolerance` 内。

Raises:
    TypeError: `fuzzySet` 不是标量模糊集，或 `tolerance` 不是实数标量。
    ValueError: `tolerance` 为负或精确高度不可得。
