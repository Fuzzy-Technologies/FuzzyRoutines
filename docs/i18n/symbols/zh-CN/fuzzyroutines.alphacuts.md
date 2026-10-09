<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

精确离散 α 截集，以及明确采用采样的连续 α 截集操作。

α 截集采用非严格边界条件 $\mu(x) \geq \alpha$。
对于 `DiscreteUniverse`，会对每个已声明坐标求值，因此结果可以精确得到。
在连续论域上，有限次检查无法精确求解任意可调用对象。
因此连续情形采用单独的采样结果，完整记录其来源，且绝不声称得到精确几何。
