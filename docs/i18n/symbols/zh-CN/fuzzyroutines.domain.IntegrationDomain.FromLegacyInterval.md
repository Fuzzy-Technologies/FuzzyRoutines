<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

映射历史二元素 `supportSet` 元组，不重新解释其含义。

Args:
    interval: 恰好包含两个数值端点的元组。

Returns:
    经过验证的闭积分域。

Raises:
    TypeError: `interval` 不是元组，或端点不是实数标量。
    ValueError: 形状、端点有限性或顺序无效。
