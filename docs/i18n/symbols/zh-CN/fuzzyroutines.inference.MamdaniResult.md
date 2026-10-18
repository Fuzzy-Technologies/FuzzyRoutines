<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

不可变的推理轨迹及可选的数值重心。

模型求值时验证轨迹的一致性。直接构造仅验证输出类型和容器的不可变性，
不重新计算记录的数学结果。

Attributes:
    inputGrades: 所有声明输入语言项隶属度的有序快照。
    rules: 有序规则激活轨迹。
    outputSet: 不附带解析证明的聚合输出模糊集。
    value: 请求计算时为重心，否则为 `None`。
    integrationDomain: 请求的重心积分区间，否则为 `None`。
    centroidPolicy: 应用的数值策略，否则为 `None`。
    method: `"adaptive-simpson"` 或 `"fuzzy-set"`。
