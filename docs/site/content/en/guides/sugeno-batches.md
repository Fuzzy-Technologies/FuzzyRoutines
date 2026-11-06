<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Evaluate Sugeno rules in batches

Install `fuzzyroutines[numpy]` and import `EvaluateSugenoBatch` to evaluate a table of observations against one built-in zero- or first-order Sugeno model. Both consequent orders can appear in the same model. Use [scalar inference](inference.md) for custom callbacks and Mamdani models.

In this monitoring example, the feed lists load before risk. Pass that column order in `featureNames`; the result keeps the original row order and describes trace columns in model declaration order. For the valid observation, the weighted firings are 0.375 and 0.25. Their normalized weights are 0.6 and 0.4, so the mean of consequences 0.25 and 0.625 is 0.4.

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

A plain real numeric array has shape `(rows, features)`. A rectangular list or tuple also works. Pass an empty list or an array of shape `(0, features)` for an empty batch. Every declared input needs a column, including load in this example.

With `onError="mask"`, use `validMask` to select predictions. Status 0 is valid, 1 marks a non-finite coordinate (including conversion overflow), 2 an input-domain violation, 3 zero firing, 4 an output-domain violation, and 5 a numerical failure. `onError="raise"` reports the first failing row by original index. Invalid shapes, names and unsupported models fail the call in either mode.

Keep `trace="off"` for values, statuses and model metadata. Choose `"summary"` for firing counts and maxima, or `"full"` to inspect term grades, rule firings and contributions. `chunkSize` limits work per chunk. Full traces retain arrays for every returned row, so their storage grows with the input.

See the [Sugeno batch API](../api/modern/sugeno-batches.md) for the entry point and result records.
