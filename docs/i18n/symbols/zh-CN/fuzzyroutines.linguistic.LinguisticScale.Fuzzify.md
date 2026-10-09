<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

根据显式的并列和置信度语义对一个坐标进行分类。

先确认坐标属于每个术语的论域，再对每个术语恰好求值一次。
结果始终公开按顺序排列的全部隶属度分数，并将最大分数记为 `confidence`。

Args:
    coordinate: 属于每个术语论域的有限标量坐标。
    policy: 显式分类策略；默认策略选择第一个精确最大值，并将零覆盖视为无匹配。

Returns:
    不可变的分数、置信度、并列记录和所选术语。

Raises:
    TypeError: `policy` 类型错误，或 `coordinate` 不是实数标量。
    ValueError: `coordinate` 不是有限值，或超出任一术语的论域。
