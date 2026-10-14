<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回以隶属度为权重的活跃语言项代表值平均。

对于隶属度 $g_i$ 和项重心 $c_i$，结果为 $\sum_i g_i c_i / \sum_i g_i$。此结果不是经截断、缩放或其他方式聚合的模糊集重心。计算后者须显式指定聚合方式及其积分域。

Args:
    grades: 按 `termNames` 排列、长度为 N 的显式元组；各有限实数隶属度均在 `[0, 1]` 内，其和不必为一。

Returns:
    采用尺度坐标单位的有限数值代表值。有理数与 binary64 隶属度及已计算重心均以精确分数累加，仅在最后将商转换为 binary64；其他实数标量使用其 binary64 表示。仅正隶属度项要求重心有定义；零隶属度项的贡献为零。

Raises:
    TypeError: 向量不是元组，或包含非实数隶属度。
    InvalidParameterError: 向量长度或隶属度无效。
    UndefinedResultError: 所有隶属度均为零、活跃项面积为零，或平均值无法表示为有限数。
    CentroidConvergenceError: 活跃项的重心计算超过限制。
