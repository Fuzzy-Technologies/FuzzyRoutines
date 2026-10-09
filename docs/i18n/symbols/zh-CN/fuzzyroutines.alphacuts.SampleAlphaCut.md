<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

在一个显式均匀网格上观察连续弱 α-截集。

结果记录坐标、经过验证的隶属度、阈值、域、分辨率和方法。它是 `isExact == False` 的采样观测，不是连续 α-截集的证明。

Args:
    fuzzySet: 连续论域上的标量模糊集。
    alpha: $[0, 1]$ 内的弱隶属度阈值。
    analysisDomain: 论域内部用于采样的有限闭区间。
    sampleCount: 均匀网格的坐标数量，包括端点。

Returns:
    带详细来源信息的采样 α-截集观测。

Raises:
    TypeError: 参数类型不符合连续约定。
    ValueError: 值无效，或采样域位于模糊集论域之外。
