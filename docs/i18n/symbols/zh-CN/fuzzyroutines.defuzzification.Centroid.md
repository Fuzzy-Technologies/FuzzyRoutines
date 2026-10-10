<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回连续隶属函数在显式有限积分域上的面积质心坐标。

结果为 $\int x\mu(x)\;\mathrm{d}x / \int \mu(x)\;\mathrm{d}x$。分段多项式和高斯 `MFunction` 来源在闭式公式稳定时使用解析面积矩；其他可调用对象使用自适应 Simpson 求积。

Args:
    fuzzySet: 不保留求值状态的连续标量模糊集。
    integrationDomain: 包含在集合论域内的有限闭区间。
    policy: 不可变的自适应容差与工作量配置。`None` 选择 [CentroidPolicy][fuzzyroutines.defuzzification.CentroidPolicy]。

Returns:
    位于 `integrationDomain` 内的有限质心坐标。

Raises:
    InvalidParameterTypeError: 集合、论域、积分域或策略类型错误。
    InvalidDomainError: 积分域超出论域。
    UndefinedResultError: 隶属面积为零，或计算得到的矩或质心不是有限值。
    CentroidConvergenceError: 自适应求积超过 `maximumDepth`。

Notes:
    假设一般可调用函数对自适应求积具有足够的正则性。若函数在采样坐标之间仍有未被分辨的局部特征，需要解析函数族或另行批准的分区域 API；不会使用固定的后备网格。
