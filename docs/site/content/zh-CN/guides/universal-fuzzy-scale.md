<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 历史通用模糊标度

**Universal Fuzzy Scale（通用模糊标度）**是 FuzzyRoutines 的历史五级预设：
**Min → Low → Med → High → Max**（最低、低、中、高、最高）。本例保留原始系数，
并展示如何用现代不可变 API 重建同一分类器。“通用”是历史名称，并不表示这些参数
适用于所有应用。它不是默认的三级 `FuzzyScale`，也不是五个等间距三角形。

[![左侧为历史五级隶属曲线，右侧为现代 API 重建；两者均保留 0.17 附近的弱覆盖区。](../../en/assets/figures/universal-fuzzy-scale.svg)](../../en/assets/figures/universal-fuzzy-scale.svg)

左图使用历史接口计算，右图使用现代接口计算。
Min 在 0.125 附近快速下降，Low、Med、High 具有平顶和二次曲线肩部，
Max 在 0.77 到 0.95 之间上升。Min 的微小正尾部仍然存在，只是在图上难以分辨。

## 原始定义

| 级别   | 历史函数族 / 现代构造函数                        | 历史 `supportSet` |
| ---- | ------------------------------------- | --------------- |
| Min  | `hyperbolic` / `Hyperbolic(8, 20, 0)` | `[0, 0.23]`     |
| Low  | `bell` / `Bell(0.17, 0.23, 0.34)`     | `[0.17, 0.40]`  |
| Med  | `bell` / `Bell(0.34, 0.40, 0.60)`     | `[0.34, 0.66]`  |
| High | `bell` / `Bell(0.60, 0.66, 0.77)`     | `[0.60, 0.83]`  |
| Max  | `parabolic` / `SShoulder(0.77, 0.95)` | `[0.77, 1]`     |

此处的 `supportSet` 是**历史质心计算的有限积分区间**。
`UniversalFuzzyScale.Fuzzy(x)` 直接调用 `mFunction.mju(x)`，**不会按该区间截断函数**。
例如，Min 在 0.23 之后仍为正。因此现代重建为所有项指定共同的闭论域 `[0,1]`。
把五个历史积分区间分别当成各项论域会改变行为，且多数输入无法完成分类。

对归一化坐标 $0\le x\le1$，先定义二次上升肩函数：

$$
s_{a,b}(x)=\begin{cases}
0,&x\le a,\\
2\left(\frac{x-a}{b-a}\right)^2,&a\lt x\le\frac{a+b}{2},\\
1-2\left(\frac{b-x}{b-a}\right)^2,&\frac{a+b}{2}\lt x\lt b,\\
1,&x\ge b.
\end{cases}
$$

$$
\mu_{\mathrm{Min}}(x)=\frac{1}{1+(8x)^{20}}
$$

$$
\mu_{\mathrm{Bell}(a,b,c)}(x)=\min\left\lbrace s_{a,b}(x),1-s_{c,c+b-a}(x)\right\rbrace
$$

$$
\mu_{\mathrm{Max}}(x)=s_{0.77,0.95}(x).
$$

钟形函数的右端点为 $c+b-a$，核为整个区间 $[b,c]$。
隶属度之和不一定为 1，也不是概率。示例与绘图测试使用这些独立公式核对数值。

## 历史接口的用法

```python
from math import isclose
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

scale = UniversalFuzzyScale()
assert [level["name"] for level in scale.levels] == ["Min", "Low", "Med", "High", "Max"]
grades = {level["name"]: level["fSet"].mFunction.mju(0.2) for level in scale.levels}
assert isclose(grades["Low"], 0.5)
assert scale.Fuzzy(0.2)["name"] == "Low"
assert scale.GetLevelByName("Med")["fSet"].supportSet == (0.34, 0.66)
assert scale.GetLevelByName("Min")["fSet"].mFunction.mju(0.5) > 0
print(grades, scale.Fuzzy(0.2)["name"])
```

兼容接口保留旧名称与构造方式。本例在 2.0 中执行，并不承诺保留 1.0.3 中的数值错误。
质心修正参见[迁移说明](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/migration/1.0.3-to-2.0.0.md)。

## 使用现代 API 显式构造

```python
from math import isclose
from fuzzyroutines import (
    Bell, ContinuousUniverse, FuzzificationPolicy, Hyperbolic,
    LinguisticScale, LinguisticTerm, ScalarFuzzySet, SShoulder,
)
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

universe = ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True)
models = (
    ("Min", Hyperbolic(8, 20, 0)),
    ("Low", Bell(0.17, 0.23, 0.34)),
    ("Med", Bell(0.34, 0.40, 0.60)),
    ("High", Bell(0.60, 0.66, 0.77)),
    ("Max", SShoulder(0.77, 0.95)),
)
scale = LinguisticScale(tuple(
    LinguisticTerm(name, ScalarFuzzySet(universe, model))
    for name, model in models
))
legacy = UniversalFuzzyScale()
policy = FuzzificationPolicy(tiePolicy="last", tieTolerance=0)
for coordinate in (0, 0.125, 0.17, 0.2, 0.37, 0.5, 0.63, 0.81, 0.86, 1):
    result = scale.Fuzzify(coordinate, policy)
    for item, previous in zip(result.memberships, legacy.levels, strict=True):
        assert isclose(item.grade, previous["fSet"].mFunction.mju(coordinate), abs_tol=1e-12)
    assert result.selectedTerms[0].name == legacy.Fuzzy(coordinate)["name"]
assert isclose(scale.Fuzzify(0.125).confidence, 0.5)
assert not scale.Fuzzify(0.17, FuzzificationPolicy(minimumConfidence=0.1)).isMatch
assert not scale.Fuzzify(0.125, FuzzificationPolicy(minimumConfidence=0.5)).isMatch
print([(item.term.name, item.grade) for item in scale.Fuzzify(0.2).memberships])
```

历史 `parabolic` 对应现代 `SShoulder`，并非无限延伸的抛物线。
保留项的顺序并设置 `tiePolicy="last"`，才能在最大值精确相等时选择后面的项。
现代默认策略选择第一个精确最大值，因此迁移时必须显式指定策略。

## 数值、边界与决策

| 坐标    | 结果 / 隶属度                          |
| ----- | --------------------------------- |
| 0     | Min = 1；包含左端点                     |
| 0.125 | Min = 0.5                         |
| 0.17  | Min ≈ 0.002129589894；Low = 0，覆盖较弱 |
| 0.20  | Low = 0.5；Min ≈ 0.000082711220    |
| 0.50  | Med = 1；Min ≈ 9.094947018 × 10⁻¹³ |
| 0.81  | High ≈ 2/9，Max ≈ 8/81；选择 High     |
| 0.86  | Max ≈ 0.5                         |
| 1     | Max = 1；包含右端点                     |

Min 与 Low 之间的弱覆盖来自历史系数，本例不调整参数。
在 0.17 处，历史分类器选择 Min，而现代策略 `minimumConfidence=0.1` 返回无匹配。
最大隶属度**等于**阈值时也返回无匹配：必须严格大于阈值。
该阈值不是分类正确的概率。

在精确实数运算中，相邻钟形函数在 0.37 和 0.63 处相等。
但浮点计算在 0.37 处得到 Low ≈ 0.5000000000000009、Med ≈ 0.4999999999999991，
所以历史选择为 **Low**。`tieTolerance=0` 保留精确比较；正容差会有意改变近似并列的处理方式。

现代示例拒绝 `[0,1]` 之外的输入。历史接口仍计算其他有限坐标，例如 −0.1 选择 Min，
1.1 选择 Max。应显式校验与归一化物理量，不要静默截断。
若要重现历史质心，也必须使用各级原有积分区间，不能统一改成 `[0,1]`。

## 复现与验证

```bash
python examples/guide.py --scenario universal-fuzzy-scale
```

示例在 **1001 个坐标** `0, 0.001, …, 1` 上用独立公式核对两种 API，
并验证标签、阈值拒绝与 Min 的正尾部。绘图测试逐一核对十条曲线各自的 **401 个坐标**。
有限网格提供回归证据，不构成对所有实数的证明。参见[图形复现](figures.md)
与[历史参数记录](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/baseline/universal-fuzzy-scale-provenance.md)。
