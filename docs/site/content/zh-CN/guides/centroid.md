<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 质心与数值精度 {#centroids-and-numerical-accuracy}

**问题：**如何用一个代表性坐标替代连续的模糊分布形状，并独立验证这个数值？

对于隶属函数下面积为正的有限积分域 $[a,b]$，

$$
c=\frac{\int_a^b x\mu(x)\,\mathrm{d}x}{\int_a^b \mu(x)\,\mathrm{d}x}.
$$


```python
from math import isclose
from fuzzyroutines import (
    Centroid, ContinuousUniverse, IntegrationDomain,
    ScalarFuzzySet, SNormPolicy, Triangle, Union,
)

universe = ContinuousUniverse(0, 8, leftClosed=True, rightClosed=True)
triangle = ScalarFuzzySet(universe, Triangle(0, 2, 8))
centroid = Centroid(triangle, IntegrationDomain(0, 8))
assert isclose(centroid, (0 + 2 + 8) / 3, abs_tol=1e-12)

combinedUniverse = ContinuousUniverse(0, 10, leftClosed=True, rightClosed=True)
left = ScalarFuzzySet(combinedUniverse, Triangle(0, 1, 3))
right = ScalarFuzzySet(combinedUniverse, Triangle(4, 6, 10))
combined = Union(left, right, SNormPolicy("logic"))
combinedCentroid = Centroid(combined, IntegrationDomain(0, 10))
assert isclose(combinedCentroid, 44 / 9, abs_tol=1e-9, rel_tol=1e-9)
print(centroid, combinedCentroid)
```


第一个三角形的几何质心为 $(0+2+8)/3=10/3\approx3.333333$。这是独立的解析基准。对于识别出的三角形函数族，库使用解析面积矩。

[![三角形质心与单独计算的四点梯形近似](../../en/assets/figures/centroid.svg)](../../en/assets/figures/centroid.svg)

青色虚线连接用户侧四个采样点 $0,8/3,16/3,8$，对应隶属度为 $0,8/9,4/9,0$。分别对面积和一阶矩应用梯形法，得到

$$
A_4=\frac{32}{9},\qquad M_4=\frac{1024}{81},\qquad
c_4=\frac{M_4}{A_4}=\frac{32}{9}\approx3.555556.
$$


绝对差为 $c_4-c=2/9$，相对差为 $(c_4-c)/c=1/15$，约 6.67%。可执行场景明确实现了该计算。**库中的 `Centroid` 不使用这套固定网格。** 图形说明了粗糙采样表示为何会改变结果。

两个不相交三角形的面积分别为 $3/2$ 和 $3$，质心分别为 $4/3$ 和 $20/3$。由于它们的支集不相交，最大值并运算可直接相加面积矩，无需重叠修正：

$$
c=\frac{(3/2)(4/3)+3(20/3)}{3/2+3}=\frac{44}{9}\approx4.888889.
$$


组合后的可调用函数使用自适应求积。所得结果与此基准在断言采用的 $10^{-9}$ 容差内一致。

**工程检查：**积分域必须位于连续论域之内。面积为零时引发 `UndefinedResultError`；自适应深度耗尽时引发 `CentroidConvergenceError`，而不是静默返回后备值。策略中的容差控制面积矩的积分，并不是质心坐标误差的已证明绝对上界。一般函数必须具有足够的规则性：仅凭有限次求值，无法排除求积过程漏掉狭窄特征。应据此选择积分域和模型。

**项目用法：**当代表性坐标影响决策时，应记录单位、有限积分边界、策略和独立参考值。截断曲线会改变所请求的质心本身。

```bash
python -I examples/guide.py --scenario centroid
```


继续阅读[尺度审查](scale-audit.md)。
