<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 从模糊规则到数值响应

设监测系统给出的归一化风险指标为 $x=0.25$，需要确定零到一之间的响应强度。
考虑两条规则：**若风险低，则响应弱**；**若风险高，则响应强**。
两条规则可以同时被激活，但激活强度不同。

在 Mamdani 系统中，各规则的结论为**输出模糊集**。先聚合这些模糊集，再计算
聚合隶属函数曲线下面积的重心。在 Sugeno 系统中，各规则的结论为**数值**，
可以是常数，也可以是输入变量的函数；系统以规则激活强度为权重求加权平均。
两种系统可以采用相同的前件逻辑，却具有不同的输出模型。

本例在 $[0,1]$ 上采用两个线性隶属函数：$\mu_L(x)=1-x$ 和 $\mu_H(x)=x$。
当 $x=0.25$ 时，隶属度为 $(0.75,0.25)$。隶属度不是事件概率。
本例的两语言项标度仅用于说明推理过程，不改变历史
[通用模糊标度](universal-fuzzy-scale.md) 的定义。

## Mamdani：聚合模糊集，再计算重心

![Mamdani 模糊推理的四个阶段](../../en/assets/figures/inference-mamdani.svg)

各规则的权重均为一，因此激活强度等于相应的输入隶属度。
最小值激活算子将两个输出隶属函数分别截断于 $0.75$ 和 $0.25$；
最大值聚合算子取其上包络：

$$
\alpha_i=w_i A_i(\mathbf{x}),\qquad
\mu_{\mathrm{out}}(y)=\max_i\min(\alpha_i,\mu_{B_i}(y)).
$$

在显式指定的区间 $D$ 上，清晰输出为该聚合隶属函数的重心：

$$
y^*=\frac{\int_D y\mu_{\mathrm{out}}(y)\,\mathrm{d}y}
{\int_D\mu_{\mathrm{out}}(y)\,\mathrm{d}y}.
$$

当 $x=0.25$ 时，上包络在 $y=0.25$ 之前为 $0.75$，随后为 $1-y$，
直到 $y=0.75$，此后为 $0.25$。面积为 $1/2$，一阶矩为 $37/192$，故
$y^*=37/96\approx0.385417$。该数值表示响应强度，而非告警正确的概率。

```python
from fuzzyroutines import (
    ContinuousUniverse, IntegrationDomain, LinguisticTerm, NegationPolicy,
    ScalarFuzzySet, SNormPolicy, TNormPolicy,
)
from fuzzyroutines.inference import (
    FuzzyVariable, InferencePolicy, MamdaniModel, MamdaniRule, TermCondition,
)

universe = ContinuousUniverse(0, 1, True, True)
terms = (
    LinguisticTerm("low", ScalarFuzzySet(universe, lambda x: 1 - x)),
    LinguisticTerm("high", ScalarFuzzySet(universe, lambda x: x)),
)
policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
model = MamdaniModel(
    (FuzzyVariable("risk", terms),), FuzzyVariable("response", terms),
    (
        MamdaniRule("low response", TermCondition("risk", "low"), "low"),
        MamdaniRule("high response", TermCondition("risk", "high"), "high"),
    ),
    policy, TNormPolicy("logic"), SNormPolicy("logic"),
)
result = model.Evaluate({"risk": 0.25}, IntegrationDomain(0, 1))
print(round(result.value, 6))  # 0.385417
print(tuple(rule.firingStrength for rule in result.rules))  # (0.75, 0.25)
```

不传入 `IntegrationDomain` 时，`Evaluate` 仅返回聚合输出集和各规则的激活输出集，
不计算重心。可对 `result.rules[i].activatedSet` 和 `result.outputSet` 采样绘图，
解释输出的形成过程。AND、OR 和 NOT 分别通过 `AllOf`、`AnyOf` 和
`NotCondition` 构造。前件合取、后件激活及输出聚合分别配置，互不混同。

## Sugeno：对数值结论加权平均

![零阶与一阶 Sugeno 规则的贡献](../../en/assets/figures/inference-sugeno.svg)

零阶 Sugeno 规则的后件为常数，例如 $(0.2,0.8)$。
一阶规则的后件为仿射函数，例如 $(x/2,0.5+x/2)$：

$$
z_i=b_i+\sum_j a_{ij}x_j,\qquad
\bar\alpha_i=\frac{\alpha_i}{\sum_k\alpha_k},\qquad
z=\sum_i\bar\alpha_i z_i.
$$

在相同的输入和激活强度下，常数后件模型得到
$0.75\cdot0.2+0.25\cdot0.8=0.35$，仿射后件模型得到
$0.75\cdot0.125+0.25\cdot0.625=0.25$。空心柱表示各规则的后件值，
实心柱表示其加权贡献；贡献之和即为输出。此过程不计算输出模糊集的面积重心。

在 `SugenoRule` 中使用 `ConstantConsequent(value)` 或
`AffineConsequent(intercept, ((inputName, coefficient), ...))`。
`SugenoModel` 要求显式指定 `outputUniverse`。每条规则的轨迹均包含
`consequentValue`、`normalizedStrength` 和 `contribution`。

安装包含该 API 的候选版本后，可运行完整的
[监测示例](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/inference.py)：

```bash
python examples/inference.py
```

示例断言三个独立计算的参考值，并以 JSON 输出输入、激活强度、后件值和贡献。
运行示例不需要图形界面或绘图库。安装 `docs/requirements-plots.txt` 后，
可用 `python -m tools.generate_inference_figures --output-directory docs/site/content/en/assets/figures`
重新生成图形；`--check` 检查生成文件是否与版本库中的文件逐字节一致。

## 组合前件并检查规则权重

以下独立示例使用与、或、非运算组合风险与负载。当 `risk=0.25`、
`load=0.75` 时，两个前件的真值为 `(0.75, 0.25)`。第一条规则的权重
`0.5` 将激活强度变为 `(0.375, 0.25)`，归一化后为 `(0.6, 0.4)`。
常数后件与仿射后件分别给出 `(0.2, 0.625)`，因此响应为 `0.37`。
这些教学规则用于展示计算过程，并非经过校准的监测策略。

```python
import math

from fuzzyroutines import (
    ContinuousUniverse, LinguisticTerm, NegationPolicy,
    ScalarFuzzySet, SNormPolicy, TNormPolicy,
)
from fuzzyroutines.inference import (
    AffineConsequent, AllOf, Antecedent, AnyOf, ConstantConsequent,
    FuzzyVariable, InferencePolicy, NotCondition,
    SugenoModel, SugenoRule, TermCondition,
)

universe = ContinuousUniverse(0, 1, True, True)
terms = (
    LinguisticTerm("low", ScalarFuzzySet(universe, lambda x: 1 - x)),
    LinguisticTerm("high", ScalarFuzzySet(universe, lambda x: x)),
)
inputs = (FuzzyVariable("risk", terms), FuzzyVariable("load", terms))
policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
busy = TermCondition("load", "high")
condition: Antecedent = AllOf((TermCondition("risk", "low"), busy))
model = SugenoModel(inputs, (
    SugenoRule("low risk and busy", condition, ConstantConsequent(0.2), weight=0.5),
    SugenoRule("risk or spare capacity", AnyOf((TermCondition("risk", "high"), NotCondition(busy))),
               AffineConsequent(0.5, (("risk", 0.5),))),
), policy, universe)
result = model.Evaluate({"risk": 0.25, "load": 0.75})
assert tuple(rule.antecedentGrade for rule in result.rules) == (0.75, 0.25)
assert tuple(rule.firingStrength for rule in result.rules) == (0.375, 0.25)
assert tuple(rule.consequentValue for rule in result.rules) == (0.2, 0.625)
assert math.isclose(result.value, 0.6 * 0.2 + 0.4 * 0.625, rel_tol=0, abs_tol=1e-15)
assert len(result.inputGrades) == 4
print(round(result.value, 2))  # 0.37
```

## 应用时应遵守的契约

每个模型具有命名的标量输入和一个标量输出。输入键必须与声明的变量名完全一致，
输入值必须有限且属于相应论域。所有规则的激活强度均为零时，抛出
`UndefinedResultError`，不会使用上次输出或默认响应。Mamdani 输出面积为零时，
无法进行重心解模糊。复合隶属函数按 `CentroidPolicy` 进行数值积分；
未达到收敛要求时，抛出 `CentroidConvergenceError`。对任意回调函数进行有限次
采样，不能保证发现采样点之间的狭窄特征。

所有 Sugeno 后件值，包括未激活规则的后件值，均须有限且属于输出论域。
溢出抛出 `NumericalError`；系统不会静默截断输出。模型容器不可变，但保留
用户隶属函数的引用；为了保证结果可复现，这些函数应为纯函数。

这些模型采用固定规则，不训练参数，也不保留自动微分计算图。
可训练的神经模糊系统需要独立的模型。完整契约见
[API 参考](../api/modern/inference.md)。

## 参考文献

- Mamdani, E. H.; Assilian, S. (1975). [An experiment in linguistic synthesis with a fuzzy logic controller](https://doi.org/10.1016/S0020-7373(75)80002-2).
- Takagi, T.; Sugeno, M. (1985). [Fuzzy identification of systems and its applications to modeling and control](https://doi.org/10.1109/TSMC.1985.6313399).

上述监测模型及计算示例为独立设计的教学内容，并非对原论文实验装置的复现。
