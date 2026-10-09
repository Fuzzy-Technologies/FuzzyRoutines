<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回论域坐标对应的、经过验证的隶属度。

Args:
    coordinate: 属于 `universe` 的有限标量坐标。

Returns:
    $[0, 1]$ 内的隶属度。

Raises:
    TypeError: 坐标或返回隶属度不是实数标量。
    ValueError: 坐标位于论域之外，或可调用对象返回非有限或越界的隶属度。
