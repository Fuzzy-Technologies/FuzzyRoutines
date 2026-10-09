<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 数值边界情况策略 {#numerical-edge-case-policy}

## 状态 {#status}

已实现的 v2 契约。任务 #64 建立此策略，任务 #66 消除了在构造时计算后会过期的质心状态，
任务 #79 和 #80 实现了[解析及自适应质心策略](../../../../mathematics/centroid-defuzzification.md)、
显式精度、收敛失败和零面积行为。

## 容差 {#tolerances}

不允许全局 epsilon。每项操作都必须具有显式数值契约：

- 隶属函数和模糊算子的代数恒等式在公式能以二进制浮点数精确表示时使用精确结果；
  否则使用具体测试规定的绝对和相对容差；
- 求根或隶属函数求逆操作声明停止准则、最大工作量和残差界限；
- 数值积分声明绝对和相对误差目标、自适应停止准则及确定性的失败方式。

## 退化输入 {#degenerate-inputs}

当必要宽度或有序断点退化时，隶属函数配置无效。
构造时必须在求值之前抛出 ValueError，不能依赖除零、零结果或稍后的缓存故障。

当声明积分域上的隶属函数面积为零时，质心解模糊化没有定义。
必须抛出 `ValueError`（现代 `UndefinedResultError` 保留此捕获契约）；
禁止返回区间中点、零、NaN、无穷或先前的缓存值。

积分精度属于积分方法的算法设置，不是隶属函数的可变配置参数。
任何硬编码的点数都不能作为正确性的依据。

## 验证依据 {#evidence}

`tests/test_numerical_edge_policy.py` 和 `tests/test_defuzzification.py`
中的测试验证已实现行为。历史的 1000 点右端点方法仅作为任务 #78 中
独立复现的历史基线依据保留。
