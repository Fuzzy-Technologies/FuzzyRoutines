<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回指定语言项在其显式积分区间上的重心。

Args:
    label: 区分大小写的完整项名；不进行前缀、近似或不区分大小写的匹配。

Returns:
    以尺度坐标单位表示的单一数值代表值。

Raises:
    TypeError: `label` 不是字符串。
    InvalidParameterError: 精确标签未知。
    UndefinedResultError: 所选项在区间上的面积为零，或存在未解析的非有限矩。
    CentroidConvergenceError: 自适应积分超过限制。
