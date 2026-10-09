<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

构成模糊集论域的一维实区间。

`None` 表示无界端点。端点是否包含必须显式指定；无界端点不能闭合，因为无穷不是实数轴的成员。

Attributes:
    left: 有限左端点，或用 `None` 表示负无穷。
    right: 有限右端点，或用 `None` 表示正无穷。
    leftClosed: 有限左端点是否属于论域。
    rightClosed: 有限右端点是否属于论域。
