<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回有限实数坐标处的标量隶属度。

Args:
    coordinate: 数学实数轴上的有限实数坐标。

Returns:
    可表示的隶属度，并保持函数族的端点规则。

Raises:
    TypeError: 坐标不是实数，或为布尔值。
    ValueError: 坐标不是有限值。
    OverflowError: 尽管坐标有限，双曲幂运算或多项式中间结果仍无法表示。
