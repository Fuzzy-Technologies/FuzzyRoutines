<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

一个尺度坐标处不可变的隶属度采样记录。

Attributes:
    coordinate: 已声明诊断网格中的有限坐标。
    memberships: 每个尺度术语的隶属度分数，按顺序排列。
    membershipThreshold: 判断空缺和重叠时使用的严格激活阈值。
