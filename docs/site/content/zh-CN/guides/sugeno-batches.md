<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 批量执行 Sugeno 规则推理

安装 `fuzzyroutines[numpy]` 并导入 `EvaluateSugenoBatch`，即可用一个采用内置函数的 Sugeno 模型处理观测表。同一模型可以同时使用零阶和一阶规则。自定义回调和 Mamdani 模型请使用[标量推理](inference.md)。

本例的监测数据先给出负载列，再给出风险列。把这个顺序传给 `featureNames`。结果按原始行顺序返回，追踪列则按模型声明顺序排列。有效行的加权激活强度为 0.375 和 0.25，归一化权重为 0.6 和 0.4，因此后件值 0.25 和 0.625 的加权平均值为 0.4。

```python
import math

from fuzzyroutines import ContinuousUniverse, LinguisticTerm, ScalarFuzzySet, Triangle
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy
from fuzzyroutines.inference import (
    AffineConsequent, ConstantConsequent, FuzzyVariable, InferencePolicy,
    SugenoModel, SugenoRule, TermCondition,
)
from fuzzyroutines.sugeno_batches import EvaluateSugenoBatch

universe = ContinuousUniverse(0, 1, True, True)
low = LinguisticTerm("low", ScalarFuzzySet(universe, Triangle(-1, 0, 1)))
high = LinguisticTerm("high", ScalarFuzzySet(universe, Triangle(0, 1, 1)))
model = SugenoModel(
    (FuzzyVariable("risk", (low, high)), FuzzyVariable("load", (low, high))),
    (
        SugenoRule("base response", TermCondition("risk", "low"), ConstantConsequent(0.25), weight=0.5),
        SugenoRule("risk response", TermCondition("risk", "high"), AffineConsequent(0.5, (("risk", 0.5),))),
    ),
    InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard")),
    universe,
)

result = EvaluateSugenoBatch(
    model,
    [[0.5, 0.25], [1.2, 0.25]],
    featureNames=("load", "risk"),
    backend="numpy",
    onError="mask",
    trace="full",
    chunkSize=1,
)
assert result.featureNames == ("risk", "load")
assert result.status.tolist() == [0, 2]
assert result.validMask.tolist() == [True, False]
assert math.isclose(result.values[0], 0.4, rel_tol=0, abs_tol=1e-12)
assert math.isnan(result.values[1])
assert result.trace.firedRuleCount.tolist() == [2, -1]
assert result.trace.full.firings[0].tolist() == [0.375, 0.25]
```

普通实数数组的形状应为 `(rows, features)`，也可以传入矩形列表或元组。空批次可用空列表或形状为 `(0, features)` 的数组表示。每个声明的输入都要有一列，本例中的负载也是如此。

设置 `onError="mask"` 后，使用 `validMask` 筛选有效预测。状态码 0 表示有效，1 表示坐标非有限（含转换溢出），2 表示输入超出论域，3 表示规则均未激活，4 表示输出超出论域，5 表示数值计算失败。`onError="raise"` 按原始行索引报告第一个失败。形状错误、名称错误或不支持的模型会在两种模式下使调用失败。

`trace="off"` 保留结果值、状态和模型元数据。`"summary"` 还提供激活规则数和最大激活强度，`"full"` 则可查看隶属度、规则激活强度和各项贡献。`chunkSize` 限制单块计算的行数。完整追踪仍为所有返回行保留数组，存储用量会随观测数增长。

入口和结果类型见 [Sugeno 批量 API](../api/modern/sugeno-batches.md)。
