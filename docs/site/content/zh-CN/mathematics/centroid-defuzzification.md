<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 质心解模糊化 {#centroid-defuzzification}

## 契约 {#contract}

对于连续标量模糊集 $A$ 及显式有限积分域 $D=[l,r]$，FuzzyRoutines 将质心定义为

$$
C(A,D)=\frac{\int_l^r x\mu_A(x)\;\mathrm{d}x}{\int_l^r \mu_A(x)\;\mathrm{d}x}.
$$

积分域是操作输入，并非集合的数学支集；它必须位于声明的 `ContinuousUniverse` 内。
分母为零或非有限值时没有质心，操作抛出 `ValueError`。

## 求值路径 {#evaluation-paths}

`Centroid` 根据隶属函数可调用对象携带的依据选择方法：

| 隶属函数来源                            | 方法                             |
| --------------------------------- | ------------------------------ |
| Triangle、trapezium、parabolic、bell | 分段多项式面积和一阶矩的解析计算               |
| 高斯形指数函数                           | 使用 `erf`/`erfc` 的解析面积及稳定的端点指数差 |
| 其他解析函数族或一般可调用对象                   | 对面积与一阶矩进行确定性的自适应 Simpson 积分    |

高斯路径对同侧尾部使用互补误差函数。
令 $u=(l-c)/s$、$v=(r-c)/s$，其中 $c$ 为中心，$s$ 为正尺度，标准化面积为

$$
I=\sqrt{\frac{\pi}{2}}
\begin{cases}
\mathrm{erfc}(u/\sqrt{2})-\mathrm{erfc}(v/\sqrt{2}), & u\ge0,\\
\mathrm{erfc}(-v/\sqrt{2})-\mathrm{erfc}(-u/\sqrt{2}), & v\le0,\\
\mathrm{erf}(v/\sqrt{2})-\mathrm{erf}(u/\sqrt{2}), & u\lt0\lt v.
\end{cases}
$$

面积为 $sI$，质心为 $c+s(e^{-u^2/2}-e^{-v^2/2})/I$。
端点差使用 `expm1`，在两个指数值接近时保留精度。
这样可以避免相减两个都已舍入到接近一的 `erf` 值。

在使用解析结果之前，归一化及特殊函数舍入的一阶误差估计必须满足调用者的
`relativeTolerance`。此估计是方法选择的保护条件，不是精确误差证明。
若面积非正或非有限、矩非有限、相减在数值上无法解析，或解析质心超出域，
则采用相同策略委托自适应积分。结果绝不截断到端点，任何路径都不会静默退回固定采样网格。

## 精度与失败 {#precision-and-failure}

`CentroidPolicy` 管理一次操作的自适应配置。默认绝对面积容差为 `1e-12`，
相对容差为 `1e-10`，每个区间最多递归二分 20 次。
一阶矩的绝对误差目标按域内最大坐标绝对值缩放。
这些是矩的误差目标，而非质心误差的直接界限。
当极小隶属度权重迫使高斯路径回退时，调用者可以显式减小绝对容差，
使它不会主导所要求的相对精度。

当配置深度无法同时满足两个矩的目标时，自适应积分抛出 `CentroidConvergenceError`。
提高限制是调用者的显式决定；失败时绝不将当前最佳估计作为已收敛结果返回。

一般可调用对象被假定具有自适应求积所需的足够正则性。
任何有限的黑箱采样都无法发现位于全部求值坐标之间的特征。
此类隶属函数需要解析函数族，或未来显式划分积分域的契约。

## 兼容门面 {#compatibility-facade}

`FuzzySet.Defuz()` 和 `defuzValue` 在每次访问时委托同一策略，
因此使用当前隶属函数参数和当前 `supportSet` 积分边界，不保留质心缓存。
`MFunction.accuracy` 为源代码兼容仍可写入，但不再控制正确性或工作量。
已退役的 1000 点右端点算法输出仍作为测试来源保留；
任务 #78 的参考用例声明绝对兼容界限为 `5e-4`。

## 验证依据 {#evidence}

- `tests/test_defuzzification.py` 覆盖独立解析参考、自适应收敛、显式不收敛、
  域验证、修改行为、狭窄解析集合及低隶属度集合；
- `tests/test_legacy_centroid_reference.py` 独立于生产代码保留退役算法的观测结果；
- `tests/test_numerical_edge_policy.py` 验证零面积时明确失败。

主导决策为 [ADR-0002](../../../../adr/0002-universe-support-semantics.md)
及 [ADR-0005](../../../../adr/0005-numerical-defuzzification-policy.md)。

## 参考文献 {#references}

- W. Van Leekwijck and E. E. Kerre, “Defuzzification: Criteria and
  Classification,” *Fuzzy Sets and Systems*, 108(2), 159–178, 1999.
  <https://doi.org/10.1016/S0165-0114(97)00337-0>
