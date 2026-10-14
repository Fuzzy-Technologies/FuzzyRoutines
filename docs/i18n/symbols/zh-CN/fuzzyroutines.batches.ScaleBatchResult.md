<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

以独立存储的只读数组描述每个坐标及有序语言项。

Attributes:
    termNames: 按标度声明顺序排列的语言项名称。
    memberships: 形状为 `input_shape + (term_count,)` 的 float64 隶属度。
    confidence: 形状为 `input_shape` 的 float64 最大隶属度。
    tied: 按策略判定的并列项布尔掩码，形状与 memberships 相同。
    selected: first/last/all 选择后的布尔掩码；未匹配时全部为 False。
    policy: 用于选择的标量分类策略。

Notes:
    构造时复制数组并设置为只读；需要修改时调用 `copy()`。隶属度为独立的程度值，不构成概率分布，也不进行逐行归一化。
