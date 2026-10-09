<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回高斯隶属函数 exp(-0.5 * ((x - center) / scale)^2)。

有限实数参数必须满足 `scale > 0`，不接受布尔值。
返回的可调用对象不可变，采用 `MembershipFunction` 所述的函数族边界约定。

Args:
    center: 高斯函数隶属度为一的峰值坐标。
    scale: 以坐标单位表示的正高斯标准差。

Returns:
    经过验证的不可变解析隶属函数。

Raises:
    ValueError: 参数不是实数、不是有限值，或违反函数族的约束。
