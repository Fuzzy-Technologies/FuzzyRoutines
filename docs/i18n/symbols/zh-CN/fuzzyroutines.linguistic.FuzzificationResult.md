<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

一次尺度分类的完整、不可变结果记录。

Attributes:
    memberships: 每个已声明尺度术语的分数，按声明顺序排列。
    confidence: 记录中的最大隶属度。
    policy: 用于确定无匹配和并列选择的策略。
    tiedTerms: 应用 `tieTolerance` 后保留的最大值术语；若置信度未超过最低阈值，
        则为空元组。
    selectedTerms: 按 `tiePolicy` 从 `tiedTerms` 中选择的术语；无匹配时为空元组。
