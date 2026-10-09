<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

按通常从左到右的参数顺序返回分段线性梯形函数。

有限实数参数必须满足 `left < plateauStart <= plateauEnd < right`，不接受布尔值。
返回的可调用对象不可变，采用 `MembershipFunction` 所述的函数族边界约定。

Args:
    left: 隶属度为零的左侧底点。
    plateauStart: 隶属度为一的平台的左端点，包含该端点。
    plateauEnd: 隶属度为一的平台的右端点，包含该端点。
    right: 形状的右边界。

Returns:
    经过验证的不可变解析隶属函数。

Raises:
    ValueError: 参数不是实数、不是有限值，或违反函数族的约束。
