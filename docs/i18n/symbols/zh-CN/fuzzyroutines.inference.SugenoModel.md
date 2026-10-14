<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

采用常数或仿射后件的标量归一化加权平均模型。

Attributes:
    inputs: 有序且不可变的输入变量元组。
    rules: 名称唯一的非空 Sugeno 规则元组。
    policy: 显式前件逻辑算子。
    outputUniverse: 各后件及最终输出的允许论域；无界连续论域允许任意有限输出。
