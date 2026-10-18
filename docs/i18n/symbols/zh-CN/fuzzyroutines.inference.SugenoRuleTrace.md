<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

一条规则的归一化标量贡献。

Attributes:
    name: 按声明顺序排列的精确规则名称。
    antecedentGrade: 类型化前件表达式的求值结果。
    weight: 声明的乘性规则权重。
    firingStrength: 权重与前件真值度的乘积。
    consequentValue: 给定输入下的常数或仿射后件值。
    normalizedStrength: 激活强度除以所有规则激活强度之和。
    contribution: 归一化激活强度与后件值的乘积。
