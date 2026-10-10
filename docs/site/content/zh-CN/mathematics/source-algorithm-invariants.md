<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 源公式与算法不变量 {#source-formula-and-algorithm-invariants}

- 状态：任务 #201 的可执行可追溯性契约
- 范围：当前已实现的标量公式及有限算法
- 事实来源：可执行代码及专门的数学契约

## 可追溯性映射 {#traceability-map}

此映射将每个非平凡实现族与其定义、边界契约、数值论证和可执行验证依据关联。
它是索引，不是详细证明的第二份副本。

| 实现领域           | 定义或推导                                                                                                                           | 必须满足的不变量                   | 可执行验证依据                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ------------------------------------------------------ |
| 历史隶属函数族        | [隶属函数契约](../../../../mathematics/membership-function-contracts.md)                                                              | 几何经过验证；稳定函数族会饱和；公式公开溢出边界   | `tests/test_formula_algorithm_invariants.py` 及隶属函数契约测试 |
| 参数化及抛物型否定      | [算子契约](../../../../adr/0004-operator-and-negation-contracts.md) 和[推导](../../../../mathematics/parabolic-negation-derivation.md) | 端点交换、不动点、单调递减和对合性          | 否定及公式不变量测试                                             |
| T 范数、s 范数和集合操作 | [显式模糊集操作](../../../../mathematics/fuzzy-set-operations.md)                                                                      | 封闭性、边界恒等式、结合律、交换律及德摩根对偶性   | 算子代数及参考测试                                              |
| 精确高度与归一化       | [高度与归一化](../../../../mathematics/fuzzy-set-normalization.md)                                                                    | 仅接受精确依据；正高度缩放为一；零高度明确失败    | 归一化及派生属性测试                                             |
| 解析及采样派生属性      | [论域与支集契约](../../../../mathematics/universe-support-contract.md)                                                                 | 解析几何精确；有限采样仍是包含完整来源的依据     | 派生属性及公式不变量测试                                           |
| 弱 α 截集与均匀采样    | [α 截集契约](../../../../mathematics/alpha-cuts.md)                                                                                 | `>=` 边界、嵌套截集、精确离散扫描及显式采样近似 | α 截集及公式不变量测试                                           |
| 相等与包含          | [相等与包含](../../../../mathematics/fuzzy-set-relations.md)                                                                         | 穷举离散比较、限定连续断言范围及显式容差       | 模糊集关系测试                                                |
| 质心解模糊化         | [数值策略](../../../../adr/0005-numerical-defuzzification-policy.md)                                                                | 解析矩或确定性自适应求积               | 解析、收敛、边界及历史参考测试                                        |

## 数值敏感分支 {#numerically-sensitive-branches}

### 抛物型否定 {#parabolic-negation}

隐式关系是关于 $d=y-x$ 的二次方程。直接计算根

$$
d = \frac{-1 + \sqrt{D}}{2(2\alpha-1)}
$$

会在 $\alpha=1/2$ 附近发生消减，并在标准补运算情形除以零。
有理化得到已实现的连续形式

$$
y = x + \frac{4(\alpha-x)}{1+\sqrt{D}}.
$$

源代码中两个判别式表达式在代数上等价，分别用于 $\alpha=1/2$ 两侧。
它们在允许域内保持各加项非负。端点处直接返回精确值，保护边界契约免受可避免的舍入影响。

### Logistic 隶属函数 {#logistic-membership}

对于 $z=a(x-b)$，当 $z$ 为绝对值很大的有限负数时，直接表达式 $1/(1+e^{-z})$ 会溢出。
因此实现使用

$$
\sigma(z) =
\begin{cases}
1/(1+e^{-z}), & z \ge 0, \\
e^z/(1+e^z), & z < 0.
\end{cases}
$$

两个指数均非正，所以 `math.exp` 不会溢出。
Binary64 仍可能将数学上属于开区间的结果舍入为精确的 `0.0` 或 `1.0`；
这是表示饱和，不是截断。

如果异号有限坐标相减发生溢出，实现计算 $ax-ab$，而不是乘以已经无穷的 $x-b$。
例如，`slope=1e-308`、`midpoint=-1e308`、`coordinate=1e308`
对应的指数接近 $2$，隶属度约为 $0.880797$，而不是溢出造成的 $1$。
此分支中按分配律展开后的乘积不会发生无穷项相消，因为原坐标异号。
普通有限相减仍保留原有算术。

### 线性斜坡与高斯距离 {#linear-ramps-and-gaussian-distances}

三角形和梯形斜坡用一个端点差除以另一个端点差。
若任一有限坐标相减溢出，在相减前将四个操作数都减半可以保持比值，
并使 binary64 差值有限。因此，`Triangle(-1e308, 1e308, 1e308)`
在零处保持隶属度 $1/2$，在包含的右顶点处保持隶属度 $1$。
普通有限差值使用既定操作；回退分支不截断隶属度。

高斯隶属函数通过无量纲距离 $(x-c)/s$ 计算 $e^{-(x-c)^2/(2s^2)}$。
若原始差值溢出，按分配律展开的除法表达式 $x/s-c/s$ 可避免丢弃有限的缩放距离。
当中心为 $-10^{308}$、尺度为 $10^{308}$、坐标为 $10^{308}$ 时，
距离为 $2$，隶属度为 $e^{-2}$，约为 $0.135335$。
真正无法表示的缩放距离仍给出可表示的零尾部。
这些保护措施与历史适配器共用相同标量核心。

### 解析求值器身份 {#analytical-evaluator-identity}

精确区域、高度、归一化和质心矩描述的是实际使用的标量求值器，不只是保存的函数族名称。
未经修改的继承 `MembershipFunction` 求值器保留内置依据。
重写 `__call__` 或其委托的 `Evaluate` 方法后，该可调用对象视为一般对象：
质心使用自适应求积，精确连续高度不可用。
单独传入规范的绑定 `Evaluate` 方法时，即使其所属对象的 `__call__` 被重写，
该方法仍保留自己的已验证依据。
历史适配器同样要求其已注册绑定求值器为规范函数族方法；
子类的自定义方法不会继承解析认证。

### Harrington 期望度 {#harrington-desirability}

公式 $d(y)=e^{-e^{-y}}$ 的数学值域为 $(0,1)$。
对于绝对值很大的有限负数 $y$，先计算内层指数会溢出，尽管最终可表示结果已是 `0.0`。
保护分支将 $y$ 与 Python 最大有限 binary64 值的对数比较，
并返回确定性的下溢极限。对于很大的有限正数 $y$，普通舍入可能产生 `1.0`。

### 历史中间结果溢出 {#historical-intermediate-overflow}

有限参数与有限输入不意味着每个 binary64 中间结果都有限。
保留的 `Hyperbolic`、`Bell` 和 `Parabolic` 表达式直接求值，不对极端幂或平方进行缩放。
因此，即使参数和输入通过有限值验证，在数值足够大时仍可能抛出 `OverflowError`。
这是当前已记录的数值限制，不是所有有限 binary64 输入均可产生隶属度的承诺。
上述稳定 Logistic 分支及 Harrington 保护处理各自已知的指数溢出路径，
不会将该保证推广到其他历史函数族。

### 均匀网格 {#uniform-grids}

对于闭区间 $[l,r]$ 和 $n\ge2$，采样操作使用

$$
h=\frac{r-l}{n-1}, \qquad x_i=l+ih.
$$

最后一个坐标直接赋值为 `r`，而不是重新计算。
因此，即使重复 binary64 算术会产生相邻值，闭域端点不变量仍精确成立。
构造和求值需要 $O(n)$ 时间及 $O(n)$ 的保留来源记录。

### 退役历史质心的依据 {#retired-legacy-centroid-evidence}

对于 `accuracy = n`，历史解模糊化计算右端点
$x_i=l+i(r-l)/n$、$i=1,\ldots,n$，并返回

$$
\frac{\sum_i x_i\mu(x_i)}{\sum_i\mu(x_i)}.
$$

共同的矩形宽度在商中消去。时间复杂度为 $O(n)$，辅助空间为 $O(1)$，
但这不是自适应求积，也不声称收敛。
测试独立保留该算法，作为任务 #78 的来源依据；它已不再是生产实现。

### 当前质心 {#current-centroid}

当前策略对受支持的分段多项式和稳定高斯路径计算解析面积及一阶矩。
其他连续可调用对象使用自适应 Simpson 求积，具有每次操作不可变的容差和有限递归限制。
零面积抛出 `ValueError`，自适应工作量耗尽抛出 `CentroidConvergenceError`；
两种情况均不会产生缓存结果、固定网格估计或当前最佳结果。
完整契约和验证依据映射见[质心解模糊化](../../../../mathematics/centroid-defuzzification.md)。

### 有限关系 {#finite-relations}

相等和包含检查在每个声明的比较坐标处最多求值一次，并在首个反例处停止。
最坏情况下时间复杂度为 $O(n)$，辅助空间为 $O(1)$。
容差相等遵循 Python 文档中的判据

$$
|a-b| \le \max(r\max(|a|,|b|), A),
$$

其中 $r$ 和 $A$ 为显式相对与绝对容差。
包含关系先接受精确序关系，仅对小幅违例的一对数值使用接近判断；
绝不以隐式 epsilon 扩大每个隶属度。

## 参考层级 {#reference-hierarchy}

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- E. P. Klement, R. Mesiar, and E. Pap, *Triangular Norms*, Springer, 2000.
  <https://doi.org/10.1007/978-94-015-9540-7>
- Python 文档，[`math` — Mathematical functions](https://docs.python.org/3/library/math.html)，
  说明 `exp`、有限数值行为及精确的 `isclose` 判据。
- C. Barker，[PEP 485 — A Function for testing approximate equality](https://peps.python.org/pep-0485/)，
  是 `math.isclose` 背后的已接受 Python 规范。
- IEEE Std 754-2019，*IEEE Standard for Floating-Point Arithmetic*。
  <https://standards.ieee.org/ieee/754/6210/>

若没有经验证的来源将精确公式与保留名称对应，历史隶属函数形状和抛物型关系
仍属于本项目特有的兼容契约。仓库明确记录这一事实，不虚构外部出处。
