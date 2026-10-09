<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

自适应质心积分的不可变误差与工作量限制。

Attributes:
    absoluteTolerance: 隶属面积的绝对误差目标。
    relativeTolerance: 两个计算矩的相对误差目标。
    maximumDepth: 单个区间递归二分的最大深度。

Notes:
    一阶矩的绝对误差目标等于 `absoluteTolerance` 乘以积分域中最大的坐标绝对值。多项式解析路径不迭代。高斯矩使用 `relativeTolerance` 拒绝精度不足的闭式减法，再交给使用同一策略的自适应积分。
