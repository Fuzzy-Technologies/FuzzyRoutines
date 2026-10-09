<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回递增的二次 S 形肩部函数，left 处为零，从 right 起为一。

有限实数参数必须满足 `left < right`，不接受布尔值。
返回的可调用对象不可变，采用 `MembershipFunction` 所述的函数族边界约定。

Args:
    left: 隶属度为零的左侧底点。
    right: 形状的右边界。

Returns:
    经过验证的不可变解析隶属函数。

Raises:
    ValueError: 参数不是实数、不是有限值，或违反函数族的约束。
