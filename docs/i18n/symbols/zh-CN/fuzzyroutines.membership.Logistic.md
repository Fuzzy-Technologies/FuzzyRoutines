<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回数值稳定的 Logistic 隶属函数，在 midpoint 处隶属度为二分之一。

有限实数参数必须满足 `slope != 0`，不接受布尔值。
返回的可调用对象不可变，采用 `MembershipFunction` 所述的函数族边界约定。

Args:
    slope: 带符号的非零斜率参数；其符号决定单调方向。
    midpoint: 隶属度为二分之一的坐标。

Returns:
    经过验证的不可变解析隶属函数。

Raises:
    ValueError: 参数不是实数、不是有限值，或违反函数族的约束。
