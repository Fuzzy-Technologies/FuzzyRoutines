<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

在均匀有限网格上返回明确标注为近似的观测结果。

Args:
    membershipFunction: 要采样标量求值结果的现代解析函数族或历史解析适配器。
    analysisDomain: 网格覆盖的有限闭区间。
    sampleCount: 均匀网格坐标数量，包含端点。

Returns:
    包含完整采样来源信息的模糊属性观测结果。

Raises:
    TypeError: 某个参数的契约类型错误。
    ValueError: `sampleCount` 小于二，或某个采样隶属度不在 $[0, 1]$ 内。
