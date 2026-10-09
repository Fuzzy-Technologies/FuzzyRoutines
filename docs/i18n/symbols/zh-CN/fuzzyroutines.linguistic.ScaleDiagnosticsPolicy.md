<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

尺度采样诊断的显式网格与容差策略。

Attributes:
    sampleCount: 等间距点的数量，包含分析域的两个端点。
    membershipThreshold: 仅当术语的隶属度严格大于此阈值时，才视为激活。
        没有激活术语表示空缺；有两个或更多激活术语表示重叠。
    partitionTolerance: 术语隶属度之和与一之间允许的最大绝对差。
