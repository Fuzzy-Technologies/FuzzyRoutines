<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

只读的批量预测值、状态和按模型声明顺序排列的元数据。

每个值、状态和有效标记对应一行原始输入。有效行的状态为零，预测值有限。失败行的状态非零，预测值为 NaN。关闭追踪时，结果不包含追踪数据。
