<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

标量模糊集的支集、核、边界和高度的计算契约。

连续解析结果由隶属函数族声明的几何形状推导，绝不通过扫描浮点值推断。
离散论域在其全部声明坐标处精确求值。
连续采样返回单独的结果类型，记录数值来源，不能与精确数学支集混淆。
