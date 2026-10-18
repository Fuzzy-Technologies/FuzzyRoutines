<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回激活输出集、聚合输出集及可选的数值重心。

Args:
    inputs: 与声明完全一致的输入名称及有限坐标。
    integrationDomain: 有限输出区间；`None` 表示仅返回模糊集。
    centroidPolicy: 自适应积分设置，需要指定积分区间。

Returns:
    不可变的轨迹快照；复合输出采用数值积分。

Raises:
    InvalidParameterError: 输入缺失、多余，或指定策略但未指定区间。
    InvalidParameterTypeError: 参数或隶属函数结果的类型错误。
    InvalidDomainError: 输入坐标或积分区间超出相应论域。
    UndefinedResultError: 无规则激活，或积分面积为零或非有限值。
    NumericalError: 正的加权规则触发强度下溢为零。
    CentroidConvergenceError: 请求的数值积分未收敛。
