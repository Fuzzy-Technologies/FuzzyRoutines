<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

一阶 Sugeno 仿射后件 $b+\sum_j a_j x_j$。

Attributes:
    intercept: 采用输出单位的有限常数项 $b$。
    coefficients: 不可变的有序 `(inputName, coefficient)` 对元组；名称必须唯一，省略的输入系数为零。
