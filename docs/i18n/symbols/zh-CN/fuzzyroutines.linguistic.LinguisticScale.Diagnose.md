<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

在一个网格上采样覆盖、重叠、空缺和分割质量。

每个术语在每个等间距网格坐标处恰好求值一次。
仅当隶属度严格大于 `membershipThreshold` 时，术语才视为激活。
此操作读取隶属函数，但绝不修改尺度术语、模糊集或解析系数。

Args:
    analysisDomain: 包含在每个术语连续论域内的有限闭区间。
    policy: 显式采样数量和容差，或默认的 101 点策略。

Returns:
    不可变的采样点记录及汇总质量指标。

Raises:
    TypeError: 域或策略的类型错误，或任一术语采用非连续论域。
    ValueError: 域超出任一术语的论域。

Notes:
    有限采样为已声明网格提供可复现的依据，
    不能证明网格点之间的覆盖或分割质量。
