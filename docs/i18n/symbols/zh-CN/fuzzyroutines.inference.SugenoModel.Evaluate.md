<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

计算所有后件值及归一化规则贡献。

Args:
    inputs: 与声明完全一致的输入名称及有限坐标。

Returns:
    包含全部有序规则贡献的不可变标量结果。

Raises:
    InvalidParameterError: 输入键或值违反契约。
    InvalidParameterTypeError: 输入或隶属度类型错误。
    InvalidDomainError: 坐标或后件值超出其论域。
    UndefinedResultError: 所有加权激活强度均为零。
    NumericalError: 正的加权规则触发强度下溢为零，或中间仿射运算、求和产生非有限值。
