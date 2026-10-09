<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回 `realValue` 处隶属度最大的级别。

出现并列时，选择尺度顺序中较后的级别。

Args:
    realValue: 由每个级别的隶属函数求值的有限内置 `int` 或 `float` 坐标；不接受 `bool`。

Returns:
    所选级别的可变字典。

Raises:
    ValueError: `realValue` 不是受支持的有限内置数值。
