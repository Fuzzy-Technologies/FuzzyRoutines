<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# JSON configuration

Install `fuzzyroutines[config]` to load and save standalone v1 JSON models.
`LoadModel` reads UTF-8 bytes into immutable scale, Mamdani, or Sugeno
definitions. `AssembleModel` binds existing runtime objects to explicit IDs,
and `DumpModel` returns canonical bytes. The caller manages file access
and invokes evaluation explicitly. Project envelopes are covered by the
project format and use a separate API contract.

A `ConfigurationError` supplies a category and an RFC 6901 JSON Pointer.
The exporter rejects custom evaluators and source numbers that would lose
precision. The validator loads on demand, so scalar use needs no extra.

This example saves two models that share a triangular scale. It checks the
Mamdani centroid and the Sugeno result after loading, then inspects an error
for duplicate JSON keys.

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
