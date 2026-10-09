<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 规范数学模型 {#canonical-mathematical-model}

本文是 FuzzyRoutines 数学契约的入口，定义通用术语，记录当前公共接口提供的公式，
并将各主题关联到详细契约和可执行验证依据。
数值算法、兼容例外和证明边界仍以各详细页面为准。

此模型是一维标量模型。多维模糊集、二型模糊集、符号代数和隐式插值不属于当前契约。

## 契约与验证依据的层级 {#contract-and-evidence-hierarchy}

当来源之间看似矛盾时，按以下顺序解释：

1. 已接受的架构决策规定预期契约；
2. 本文陈述整合后的数学模型；
3. 专门的数学页面规定各主题的细节和验证依据的边界；
4. 公共文档字符串描述可调用对象的行为；
5. 可执行测试验证当前实现的行为。

[当前实现状态](../../../../current-status.md) 区分已接受的设计和实际提供的行为。
[历史兼容契约](../../../../compatibility/legacy-public-api-1.0.3.md) 保护现有名称与签名，
但不会使历史术语成为数学上的规范术语。

## 标量模糊集与域 {#scalar-fuzzy-set-and-domains}

标量模糊集是有序对

$$
A=(X,\mu_A), \qquad \mu_A:X\to[0,1],
$$

其中 $X$ 是显式声明的 `ContinuousUniverse` 或 `DiscreteUniverse`。
坐标与隶属度均为有限实数标量。布尔值、非有限值及超出范围的隶属度会被拒绝，不会被强制转换。

必须区分以下概念：

| 概念     | 定义                                 | 当前表示                                      |
| ------ | ---------------------------------- | ----------------------------------------- |
| 论域     | $\mu_A$ 定义 $A$ 的坐标集合               | `ContinuousUniverse` 或 `DiscreteUniverse` |
| 积分域    | 一次数值操作使用的有限闭区间                     | `IntegrationDomain`                       |
| 模糊集的支集 | $\{x\in X\mid\mu_A(x)\gt 0\}$      | 精确区域或显式采样记录                               |
| 支集闭包   | 支集相对于 $X$ 的闭包                      | 受支持表示的精确区域                                |
| 模糊集的核  | $\{x\in X\mid\mu_A(x)=1\}$         | 受支持表示的精确区域                                |
| 边界     | $\{x\in X\mid0\lt \mu_A(x)\lt 1\}$ | 模糊过渡区域，并非拓扑边界                             |
| 高度     | $\sup\{\mu_A(x)\mid x\in X\}$      | 仅在表示能够提供证明时才是精确标量                         |

绝不将积分域推断为支集。特别是，历史 `FuzzySet.supportSet` 元组只是有限积分区间的兼容名称。
精确属性和采样属性的语义由[论域与支集契约](../../../../mathematics/universe-support-contract.md)
及 [ADR-0002](../../../../adr/0002-universe-support-semantics.md) 规定。

## 隶属函数族 {#membership-function-families}

`MFunction` 是历史解析函数族注册表。令 $S_{a,b}$ 表示二次递增肩部函数

$$
S_{a,b}(x)=
\begin{cases}
0, & x\le a,\\
2\left(\dfrac{x-a}{b-a}\right)^2, & a\lt x\le\dfrac{a+b}{2},\\
1-2\left(\dfrac{x-b}{b-a}\right)^2, & \dfrac{a+b}{2}\lt x\lt b,\\
1, & x\ge b.
\end{cases}
$$

triangle 和 trapezium 函数族使用受保护的历史参数顺序，尽管其几何断点顺序不同：

$$
\mathrm{Tri}_{a,c,b}(x)=
\begin{cases}
0, & x\le a,\\
\dfrac{x-a}{c-a}, & a\lt x\le c,\\
\dfrac{b-x}{b-c}, & c\lt x\le b,\\
0, & x\gt b,
\end{cases}
$$

以及

$$
\mathrm{Trap}_{a,c,d,b}(x)=
\begin{cases}
0, & x\le a,\\
\dfrac{x-a}{c-a}, & a\lt x\lt c,\\
1, & c\le x\le d,\\
\dfrac{b-x}{b-d}, & d\lt x\le b,\\
0, & x\gt b.
\end{cases}
$$

每个保存的隶属函数参数均为有限的内置 `int` 或 `float`；
尽管 Python 将布尔值视为整数，这里仍拒绝布尔值。
以下函数族专有约束是在此通用标量契约之上的附加要求。
`desirability` 不保存参数，但其求值坐标仍必须是有限内置标量。

已实现的函数族如下：

| 历史标识符          | 数学函数                                                                     | 有效参数                                  | 完全等价的别名                  |
| -------------- | ------------------------------------------------------------------------ | ------------------------------------- | ------------------------ |
| `hyperbolic`   | 当 $x\le c$ 时为 $1$；否则为 $1/(1+(a(x-c))^b)$                                 | $a\gt 0$、$b\gt 0$，且 $c$ 有限            | 无                        |
| `bell`         | 当 $x\lt b$ 时为 $S_{a,b}(x)$；在 $[b,c]$ 上为 $1$；超过 $c$ 后为 $1-S_{c,c+b-a}(x)$ | $a\lt b\le c$                         | 无                        |
| `parabolic`    | $S_{a,b}(x)$                                                             | $a\lt b$                              | `sShoulder`              |
| `triangle`     | $\mathrm{Tri}_{a,c,b}(x)$                                                | $a\lt c\le b$；历史顺序为 `a, b, c`         | 无                        |
| `trapezium`    | $\mathrm{Trap}_{a,c,d,b}(x)$                                             | $a\lt c\le d\lt b$；历史顺序为 `a, b, c, d` | 无                        |
| `exponential`  | $\exp\!\left[-\tfrac12((x-a)/b)^2\right]$                                | $a$ 有限，$b\gt 0$                       | `gaussian`               |
| `sigmoidal`    | $1/(1+\exp[-a(x-b)])$                                                    | $a\ne0$，且 $b$ 有限                      | `logistic`               |
| `desirability` | $\exp[-\exp(-y)]$                                                        | $y$ 有限；无保存的参数                         | `harringtonDesirability` |

triangle 和 trapezium 的精确分段方程、数值分支及历史参数顺序
由[隶属函数契约](../../../../mathematics/membership-function-contracts.md) 固定。
历史 `bell` 是平顶分段二次函数族，不是其他库中常见的广义钟形函数。
注册表别名共用同一实现；它们不是新函数族，也不意味着可以重命名受保护的参数。

## 否定 {#negations}

每个否定都将 $[0,1]$ 映射到 $[0,1]$。
现代集合 API 要求显式 `NegationPolicy`，没有进程级默认值。

标准补运算为

$$
N(x)=1-x.
$$

历史参数化强否定的不动点为 $\alpha\in(0,1)$：

$$
N_\alpha(x)=
\begin{cases}
1+x\dfrac{\alpha-1}{\alpha}, & x\le\alpha,\\
(x-1)\dfrac{\alpha}{\alpha-1}, & x\gt \alpha.
\end{cases}
$$

抛物型函数族是以下方程的有效分支

$$
2\alpha-x-y=(2\alpha-1)(y-x)^2,
\qquad \alpha\in\left[\frac14,\frac34\right].
$$

令 $D=1-8(2\alpha-1)(x-\alpha)$，抗消减误差的分支为

$$
N_\alpha(x)=x+\frac{4(\alpha-x)}{1+\sqrt{D}}.
$$

在允许域内，它满足 $N(0)=1$、$N(1)=0$、$N(\alpha)=\alpha$、单调递减和对合性。
`FuzzyNOTParabolic` 保留的 `epsilon` 参数仅用于兼容，不控制解析算法。
参见[推导](../../../../mathematics/parabolic-negation-derivation.md)
及 [ADR-0004](../../../../adr/0004-operator-and-negation-contracts.md)。

## T 范数与 s 范数 {#t-norms-and-s-norms}

对于 $x,y\in[0,1]$，公共标量算子和现代策略值提供四个对偶函数族。
第一列的代码值是受保护的历史注册表标识符，不是标准数学函数族名称：

| 历史标识符       | t 范数标准名称       | T 范数 $T(x,y)$                         | s 范数标准名称       | S 范数 $S(x,y)$                         |
| ----------- | -------------- | ------------------------------------- | -------------- | ------------------------------------- |
| `logic`     | 最小值            | $\min(x,y)$                           | 最大值            | $\max(x,y)$                           |
| `algebraic` | 乘积             | $xy$                                  | 概率和（代数和）       | $x+y-xy$                              |
| `boundary`  | Łukasiewicz 范数 | $\max(x+y-1,0)$                       | Łukasiewicz 范数 | $\min(x+y,1)$                         |
| `drastic`   | 剧烈积            | 当 $x=1$ 时为 $y$；当 $y=1$ 时为 $x$；否则为 $0$ | 剧烈和            | 当 $x=0$ 时为 $y$；当 $y=0$ 时为 $x$；否则为 $1$ |

历史拼写为 `SCoNorm`；现代集合策略为 `SNormPolicy`。
组合操作在折叠之前验证每个操作数。可执行测试套件验证封闭性、交换律、结合律、
单位元以及标准否定下的两条德摩根定律。

## 模糊集代数 {#fuzzy-set-algebra}

所有现代二元操作都要求论域精确相等，绝不隐式推断重采样网格、坐标转换或论域协调方式。

对于同一论域上的集合 $A$ 和 $B$：

$$
\begin{aligned}
\mu_{\neg A}(x) &= N(\mu_A(x)),\\
\mu_{A\cap B}(x) &= T(\mu_A(x),\mu_B(x)),\\
\mu_{A\cup B}(x) &= S(\mu_A(x),\mu_B(x)),\\
\mu_{A\setminus B}(x) &= T(\mu_A(x),N(\mu_B(x))).
\end{aligned}
$$

差集是有方向的。对于一般模糊隶属度，$A\setminus A$ 不一定为空。
对称差集尚未纳入公共契约，因为还需要显式的 s 范数和已接受的组合策略。
参见[显式模糊集操作](../../../../mathematics/fuzzy-set-operations.md)。

数学相等与包含也是显式操作：

$$
\begin{aligned}
A=B &\iff \forall x\in X:\mu_A(x)=\mu_B(x),\\
A\subseteq B &\iff \forall x\in X:\mu_A(x)\le\mu_B(x).
\end{aligned}
$$

离散论域会被穷举检查。任意连续可调用对象要求声明有限的 `ComparisonDomain`，
因此肯定结果仅对这些坐标提供依据，不能证明全局函数相等。
精确策略和容差策略绝不隐式选择。
参见[相等与包含](../../../../mathematics/fuzzy-set-relations.md)。

## α 截集、高度、归一化与凸性 {#alpha-cuts-height-normalization-and-convexity}

FuzzyRoutines 使用弱 α 截集：

$$
A_\alpha=\{x\in X\mid\mu_A(x)\ge\alpha\},
\qquad \alpha\in[0,1].
$$

因此 $A_0=X$，$A_1$ 为核，且当 $0\le\alpha\le\beta\le1$ 时
有 $A_\beta\subseteq A_\alpha$。
对于声明的有限 `DiscreteUniverse`，`AlphaCut` 是精确的。
`SampleAlphaCut` 记录有限连续网格，并始终报告 `isExact == False`；
其结果不是连续几何。

对于精确的正高度 $h(A)$，归一化定义为

$$
\mu_{\mathrm{Normalize}(A)}(x)=\frac{\mu_A(x)}{h(A)}.
$$

高度为零时会被拒绝。精确高度可通过穷举离散集合，或受支持的解析连续函数族获得。
对于任意连续可调用对象，操作会明确失败，不会把采样最大值用作证明。
参见 [α 截集契约](../../../../mathematics/alpha-cuts.md)
和[归一化契约](../../../../mathematics/fuzzy-set-normalization.md)。

已接受的一维凸性定义为拟凹性：

$$
\mu_A(\lambda x+(1-\lambda)y)
\ge\min(\mu_A(x),\mu_A(y)),
\qquad \lambda\in[0,1].
$$

等价地，每个正水平的弱 α 截集都为凸集。
此定义已由 [ADR-0009](../../../../adr/0009-fuzzy-set-convexity-semantics.md) 接受，
但公共凸性查询及带验证依据的结果 API **尚未实现**。
有限连续网格可以发现反例；没有采样到违例不能证明全局凸性。
参见[凸性设计契约](../../../../mathematics/fuzzy-set-convexity.md)。

## 语言术语与尺度 {#linguistic-terms-and-scales}

现代表述将一个精确的非空名称与一个 `ScalarFuzzySet` 关联：

$$
L=(\text{name},A).
$$

`LinguisticScale` 保存非空有序的 `LinguisticTerm` 元组，
其名称在 Unicode 不区分大小写比较下唯一。精确查找保留大小写；
可选的不区分大小写查找比较经过大小写折叠的完整名称。
`Fuzzify()` 返回所有按顺序排列的隶属度分数，并以最大值作为置信度。
显式 `FuzzificationPolicy` 定义最低置信度、绝对并列容差，
以及按顺序选择 `first`、`last` 或 `all` 的并列处理方式。
主导契约为 [ADR-0013](../../../../adr/0013-linguistic-fuzzification-policy.md)。

`Diagnose()` 在显式、保留端点的有限网格上求值，记录各点的最大隶属度、
激活术语、空缺、重叠和单位分解误差。其域、采样数量、激活阈值和分解容差均显式给出。
结果是可复现的采样依据，绝不声称证明网格点之间的连续性质。
诊断定义及不修改对象的边界由 [ADR-0014](../../../../adr/0014-sampled-scale-diagnostics.md) 固定。

历史可变列表 `FuzzyScale.levels` 仍作为兼容接口提供，
`GetLevelByName()` 保留历史调用形式。原有 `Fuzzy()` 的后者胜出行为仍受支持，
在带类型模型中对应显式的 `last` 策略。
参见[语言术语表示](../../../../mathematics/linguistic-term-model.md)。

## 质心解模糊化 {#centroid-defuzzification}

对于连续模糊集及显式有限积分域 $D=[l,r]$，已实现的质心为

$$
C(A,D)=
\frac{\int_l^r x\mu_A(x)\,\mathrm{d}x}
     {\int_l^r \mu_A(x)\,\mathrm{d}x}.
$$

多项式函数族使用解析矩。对于高斯隶属函数，只要有限面积可在数值上解析，
就使用稳定的闭式表达式。其他 `MFunction` 函数族和一般可调用对象使用
确定性的自适应 Simpson 积分，并显式指定 `CentroidPolicy`。
零面积或非有限面积抛出 `ValueError`；自适应工作量耗尽时抛出 `CentroidConvergenceError`。
绝不会把当前最佳估计或固定网格估计作为已收敛结果返回。

兼容方法 `FuzzySet.Defuz()` 和属性 `defuzValue` 在每次访问时委托此策略，
使用当前参数与当前 `supportSet` 积分边界，不保留质心缓存。
参见[质心契约](../../../../mathematics/centroid-defuzzification.md)
及 [ADR-0005](../../../../adr/0005-numerical-defuzzification-policy.md)。

## 实现边界 {#implementation-boundary}

| 能力                | 状态      | 契约或验证依据                                                             |
| ----------------- | ------- | ------------------------------------------------------------------- |
| 显式连续及离散论域         | 已实现     | [论域与支集](../../../../mathematics/universe-support-contract.md)       |
| 历史解析隶属函数注册表       | 已实现并受保护 | [隶属函数](../../../../mathematics/membership-function-contracts.md)    |
| 显式否定、t 范数和 s 范数策略 | 已实现     | [ADR-0004](../../../../adr/0004-operator-and-negation-contracts.md) |
| 补集、交集、并集和差集       | 已实现     | [模糊集操作](../../../../mathematics/fuzzy-set-operations.md)            |
| 相等与包含             | 已实现     | [关系](../../../../mathematics/fuzzy-set-relations.md)                |
| 精确离散截集和采样连续截集     | 已实现     | [α 截集](../../../../mathematics/alpha-cuts.md)                       |
| 高度与归一化            | 已实现     | [归一化](../../../../mathematics/fuzzy-set-normalization.md)           |
| 带类型的语言表示          | 已实现     | [语言术语](../../../../mathematics/linguistic-term-model.md)            |
| 尺度采样诊断            | 已实现     | [语言术语](../../../../mathematics/linguistic-term-model.md)            |
| 解析及自适应质心          | 已实现     | [质心解模糊化](../../../../mathematics/centroid-defuzzification.md)       |
| 可执行凸性结果 API       | 规划中     | [已接受的设计](../../../../mathematics/fuzzy-set-convexity.md)            |
| 带类型的语言查找与模糊化      | 已实现     | [语言术语](../../../../mathematics/linguistic-term-model.md)            |
| 对称差集              | 不支持     | [ADR-0008](../../../../adr/0008-fuzzy-set-difference-semantics.md)  |
| 多维或二型模糊集          | 范围之外    | 需要单独的架构决策                                                           |

## 详细契约索引 {#detailed-contract-index}

| 主题     | 规范详细说明                                                              |
| ------ | ------------------------------------------------------------------- |
| 有限标量值  | [有限数值策略](../../../../mathematics/finite-number-policy.md)           |
| 数值容差   | [数值边界策略](../../../../mathematics/numerical-edge-policy.md)          |
| 域与派生几何 | [论域与支集](../../../../mathematics/universe-support-contract.md)       |
| 隶属函数族  | [公式与参数契约](../../../../mathematics/membership-function-contracts.md) |
| 稳定数值分支 | [源公式与算法不变量](../../../../mathematics/source-algorithm-invariants.md) |
| 否定     | [抛物型推导](../../../../mathematics/parabolic-negation-derivation.md)   |
| 集合操作   | [补集、交集、并集和差集](../../../../mathematics/fuzzy-set-operations.md)      |
| 关系     | [相等与包含](../../../../mathematics/fuzzy-set-relations.md)             |
| α 截集   | [精确与采样 α 截集](../../../../mathematics/alpha-cuts.md)                 |
| 高度与归一化 | [模糊集归一化](../../../../mathematics/fuzzy-set-normalization.md)        |
| 凸性     | [模糊集凸性](../../../../mathematics/fuzzy-set-convexity.md)             |
| 语言模型   | [带类型的语言术语表示](../../../../mathematics/linguistic-term-model.md)      |
| 解模糊化   | [质心解模糊化](../../../../mathematics/centroid-defuzzification.md)       |
| 兼容性    | [从历史 API 迁移到现代 API](../../../../migration/historical-to-modern.md)  |

## 许可证 {#license}

本文档采用 [Apache 许可证 2.0](../../../../../LICENSE)。
重新分发时必须保留 [NOTICE](../../../../../NOTICE) 中规定的许可证、版权和署名声明。
