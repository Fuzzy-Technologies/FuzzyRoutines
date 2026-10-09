<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回递减的双曲尾部函数，坐标不大于 cutoff 时隶属度为一。

有限实数参数必须满足 `scale > 0 and exponent > 0`，不接受布尔值。
返回的可调用对象不可变，采用 `MembershipFunction` 所述的函数族边界约定。

Args:
    scale: 截止点之外距离的正乘数。
    exponent: 双曲尾部的正幂指数。
    cutoff: 隶属度为一的左肩部的结束位置。

Returns:
    经过验证的不可变解析隶属函数。

Raises:
    ValueError: 参数不是实数、不是有限值，或违反函数族的约束。
