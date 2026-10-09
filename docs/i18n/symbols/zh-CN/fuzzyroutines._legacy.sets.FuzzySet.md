<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

表示可变的历史模糊集及其积分区间。

Args:
    membershipFunction: 已配置的 [MFunction][fuzzyroutines.FuzzyRoutines.MFunction]。
    supportSet: 用作数值积分域的二元素元组。
    linguisticName: 可读的集合名称。

Raises:
    Exception: `linguisticName` 不是字符串，或 `membershipFunction` 不是 `MFunction`。
    TypeError: `supportSet` 不是元组，或包含非实数端点。
    ValueError: `supportSet` 不包含两个有限且严格递增的端点。

Notes:
    历史名称 `supportSet` 表示积分边界，而非精确数学支集。
    新代码应使用 [ScalarFuzzySet][fuzzyroutines.ScalarFuzzySet]。
