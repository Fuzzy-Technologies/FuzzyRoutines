<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# JSON 配置 {#json-configuration}

安装 `fuzzyroutines[config]` 即可加载和保存独立的版本 1 JSON 模型。
`LoadModel` 读取 UTF-8 字节并返回不可变的标度、Mamdani 或 Sugeno 定义。
`AssembleModel` 将现有运行时对象绑定到显式 ID，`DumpModel` 返回规范化字节。
文件访问和模型求值由调用方显式控制。项目文档采用独立的接口契约。

`ConfigurationError` 提供错误类别和 RFC 6901 JSON 指针。导出器会拒绝
自定义求值器及无法无损表示的数值。验证器按需加载，标量计算无需安装此扩展。

示例保存共享三角标度的两个模型。加载后检查 Mamdani 质心与 Sugeno 结果，
然后检查重复 JSON 键所产生的错误。

```python
from fuzzyroutines import (
    CentroidPolicy, ContinuousUniverse, IntegrationDomain, LinguisticScale,
    LinguisticTerm, NegationPolicy, ScalarFuzzySet, SNormPolicy, TNormPolicy, Triangle,
)
from fuzzyroutines.configuration import (
    AssembleModel, ConfigurationError, DumpModel, LoadModel, MamdaniBinding,
    MamdaniCentroid, ScaleDefinition, ScaleRepresentatives, SugenoBinding,
)
from fuzzyroutines.inference import (
    ConstantConsequent, FuzzyVariable, InferencePolicy, MamdaniModel,
    MamdaniRule, SugenoModel, SugenoRule, TermCondition,
)

universe = ContinuousUniverse(0, 1, True, True)
membership = Triangle(0, 0.5, 1)
term = LinguisticTerm("Middle", ScalarFuzzySet(universe, membership))
window = IntegrationDomain(0, 1)
centroidPolicy = CentroidPolicy()
scale = ScaleDefinition(
    LinguisticScale((term,)), "unit", ("middle",), ("triangle",),
    representatives=ScaleRepresentatives((window,), centroidPolicy),
)
variable = FuzzyVariable("Risk", (term,))
output = FuzzyVariable("Response", (term,))
condition = TermCondition("Risk", "Middle")
policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
mamdani = MamdaniModel(
    (variable,), output, (MamdaniRule("Respond", condition, "Middle"),),
    policy, TNormPolicy("logic"), SNormPolicy("logic"),
)
sugeno = SugenoModel(
    (variable,), (SugenoRule("Respond", condition, ConstantConsequent(0.25)),), policy, universe,
)
inputs = (("risk", "scale"),)
rules = ("respond",)
bindings = (
    MamdaniBinding(mamdani, inputs, rules, "response", "scale", MamdaniCentroid(window, centroidPolicy)),
    SugenoBinding(sugeno, inputs, rules, "unit"),
)

for binding in bindings:
    model = AssembleModel({"unit": universe}, {"triangle": membership}, {"scale": scale}, inference=binding)
    encoded = DumpModel(model)
    loaded = LoadModel(encoded)
    assert DumpModel(loaded) == encoded
    inference = loaded.inference

    if isinstance(inference, MamdaniBinding):
        assert inference.centroid is not None
        result = inference.model.Evaluate({"Risk": 0.25}, inference.centroid.domain, inference.centroid.policy)
        assert abs(result.value - 0.5) < 1e-12
    else:
        assert isinstance(inference, SugenoBinding)
        result = inference.model.Evaluate({"Risk": 0.25})
        assert result.value == 0.25

    assert result.rules[0].firingStrength == 0.5

try:
    LoadModel(b'{"kind":"model","kind":"model"}')
except ConfigurationError as error:
    assert (error.category, error.pointer) == ("malformed-document", "/kind")
else:
    raise AssertionError("Expected duplicate JSON keys to fail.")
```

::: fuzzyroutines.configuration
    options:
      members:
        - LoadModel
        - DumpModel
        - AssembleModel
        - ModelConfiguration
        - ScaleDefinition
        - ScaleRepresentatives
        - MamdaniBinding
        - MamdaniCentroid
        - SugenoBinding
        - ConfigurationError
