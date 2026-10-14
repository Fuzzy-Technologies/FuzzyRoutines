<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

后件为常数或仿射标量表达式的命名规则。

Attributes:
    name: 唯一规则标识符，结果保持声明顺序。
    antecedent: 由输入语言项构成的类型化表达式。
    consequent: 显式零阶或一阶后件。
    weight: $[0,1]$ 内的有限权重，与前件真值度相乘。
