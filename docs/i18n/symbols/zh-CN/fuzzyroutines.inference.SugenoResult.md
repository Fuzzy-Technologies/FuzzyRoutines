<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

不可变的加权平均结果及有序规则贡献。

模型求值时验证一致性；直接构造仅验证容器不可变性及输出有限性，
不验证记录的数学结果。

由于舍入，轨迹中贡献的总和可能与 `value` 略有差异。若总和超出后件值的凸包，
则通过精确有理数运算重新计算加权平均，使结果保持在该凸包内。

Attributes:
    inputGrades: 所有声明输入语言项隶属度的有序快照。
    rules: 有序标量规则轨迹，包括未激活的规则。
    value: 有限的归一化加权平均输出。
    method: 固定标识符 `"normalized-weighted-average"`。
