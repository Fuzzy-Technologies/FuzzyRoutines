<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

具有显式后件激活及输出聚合策略的标量规则库。

Attributes:
    inputs: 有序且不可变的输入变量元组。
    output: 命名输出变量，其语言项共享连续论域。
    rules: 名称唯一的非空 Mamdani 规则元组。
    policy: 显式前件逻辑算子。
    activation: 将激活强度作用于各后件模糊集的 t-范数。
    aggregation: 合并激活输出集的 s-范数。
