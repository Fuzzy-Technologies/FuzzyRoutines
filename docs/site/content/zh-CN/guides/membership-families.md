<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 选择隶属函数族 {#choose-a-membership-family}

根据概念的含义选择曲线：容差带、平滑过渡、中心偏好或单调尾部。工厂函数返回不可变的 `MembershipFunction` 对象，不会根据数据拟合参数。所有坐标和参数必须满足文档规定的有限实数约定；布尔值不作为数值接受。

[![由标量 API 求值的八类隶属函数](../../en/assets/figures/membership-families.svg)](../../en/assets/figures/membership-families.svg)

每条曲线显示 −3 至 3 之间的 401 个观测值。显示区间不等于数学支集的范围；高斯、Logistic、期望度和双曲函数的尾部延伸到区间之外。远处坐标的数值下溢不会重新定义解析函数族的支集。

## Hyperbolic：饱和区与递减尾部 {#hyperbolic-saturation-followed-by-a-decreasing-tail}

`Hyperbolic(scale, exponent, cutoff)` 在不高于 `cutoff` 时为一，之后递减。正的尺度和指数决定尾部形状。示意惩罚模型可采用 `Hyperbolic(1, 2, 0)`；坐标为 1 时，隶属度为 0.5。

## Bell：平滑的有限容差带 {#bell-a-smooth-finite-tolerance-band}

`Bell(left, plateauStart, plateauEnd)` 具有二次肩部和平坦平台。右底点为 `plateauEnd + plateauStart - left`；它不是高斯函数。对于 `Bell(-2, -1, 1)`，平台为 [−1, 1]，右底点为 2。

## SShoulder：平滑过渡至饱和 {#s-shoulder-a-smooth-transition-to-saturation}

`SShoulder(left, right)` 在不高于 `left` 时为零，不低于 `right` 时为一，中间采用二次变化。中点隶属度为 0.5。适用于随数值增加、逐渐完全符合某概念的情况。

## Triangle：具有线性容差的偏好值 {#triangle-a-preferred-value-with-linear-tolerance}

`Triangle(left, peak, right)` 采用通常的左端—峰值—右端顺序。要求 `left < peak <= right`，允许峰值位于右端点。对称三角形便于表达偏好的设置，非对称容差同样有效。质量场景使用 `Triangle(10, 12, 14)`。

## Trapezoid：完全可接受的区间 {#trapezoid-a-fully-acceptable-interval}

`Trapezoid(left, plateauStart, plateauEnd, right)` 具有线性肩部和隶属度为一的区间，允许 `plateauStart == plateauEnd`。适用于一段设置范围同样可接受、而非只偏好单点的情形。

## Gaussian：围绕中心的平滑偏好 {#gaussian-smooth-preference-around-a-center}

`Gaussian(center, scale)` 计算未作概率归一化的隶属曲线

$$
\mu(x)=\exp\left[-\frac12\left(\frac{x-\mathrm{center}}{\mathrm{scale}}\right)^2\right].
$$


尺度为正，峰值为一。这是隶属函数，而不是归一化概率密度；其面积不必等于一。

## Logistic：单调 S 形曲线 {#logistic-a-monotone-sigmoid}

`Logistic(slope, midpoint)` 在中点的隶属度为 0.5。斜率必须非零：正斜率递增，负斜率递减。数学上任何有限坐标都达不到极限隶属度零或一，但浮点计算可能因舍入或下溢而得到端点值。

## HarringtonDesirability：固定的非对称 S 形曲线 {#harrington-desirability-a-fixed-asymmetric-sigmoid}

`HarringtonDesirability()` 没有参数，计算

$$
\mu(x)=\exp[-\exp(-x)].
$$


输入是经过变换的无量纲期望度坐标。在传入物理测量值之前，应先在模型中定义这种变换。在零点，隶属度为 $\exp(-1)$，约为 0.367879。

## 执行所有函数族并查看不可变定义 {#execute-every-family-and-inspect-an-immutable-definition}

```python
from math import exp, isclose
from fuzzyroutines import (
    Bell, Gaussian, HarringtonDesirability, Hyperbolic, Logistic,
    MembershipFunction, SShoulder, Trapezoid, Triangle,
)

assert Hyperbolic(1, 2, 0)(1) == 0.5
assert Bell(-2, -1, 1)(0) == 1
assert SShoulder(-2, 2)(0) == 0.5
assert Triangle(-2, 0, 2)(0) == 1
assert Trapezoid(-2, -1, 1, 2)(0) == 1
assert Gaussian(0, 1)(0) == 1
assert Logistic(2, 0)(0) == 0.5
assert isclose(HarringtonDesirability()(0), exp(-1))
definition = MembershipFunction("triangle", left=-2, peak=0, right=2)
assert definition.Evaluate(0) == definition(0) == 1
assert definition.family == "triangle" and definition.parameters["peak"] == 0
print(definition.family, dict(definition.parameters))
```


工厂函数是最方便的入口。通用构造函数要求精确的规范函数族标识符和参数名，包括 `"s_shoulder"` 和 `"harrington_desirability"`。这些字符串是数据，不是 Python 声明名称。完整的有效性约束请参阅[隶属函数 API](../api/modern/membership.md)。

对于这些函数族无法表达的模型，可使用[带类型的自定义求值器](custom.md)。精确连续性质需要解析依据；任意可调用函数不会仅因曲线形似某个已知函数而获得这种依据。
