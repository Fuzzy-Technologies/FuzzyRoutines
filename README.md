<!--
SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

<p align="center">
  <img src="https://raw.githubusercontent.com/Fuzzy-Technologies/FuzzyRoutines/master/docs/site/content/en/assets/brand/fuzzyroutines-alice.png" alt="Alice in the Fuzzy Technologies research laboratory" width="640">
</p>

# FuzzyRoutines

Turn measurements into interpretable linguistic grades with explicit fuzzy mathematics.

Classify measurements, combine fuzzy criteria, inspect sets and explain results.
**CPython 3.13–3.14 · no mandatory runtime dependencies · Apache-2.0**

[Documentation](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/) ·
[Русский](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/ru/) ·
[简体中文](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/zh-CN/)

## Try it: is 24 °C comfortable or warm?

This source describes **FuzzyRoutines 2.1.0**. Install that exact version:

```console
python -m pip install fuzzyroutines==2.1.0
```

If 2.1.0 is not yet available on PyPI, install the reviewed CI wheel using the
[version-aware agent guide](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/site/content/en/agent-quickstart.md).
The [published 2.0.0 baseline](https://pypi.org/project/fuzzyroutines/2.0.0/)
remains available for reproducing earlier results.

```python
from fuzzyroutines import (
    ContinuousUniverse, LinguisticScale, LinguisticTerm,
    ScalarFuzzySet, SShoulder, Triangle,
)

universe = ContinuousUniverse(0, 40, leftClosed=True, rightClosed=True)
scale = LinguisticScale((
    LinguisticTerm("Comfort", ScalarFuzzySet(universe, Triangle(16, 22, 28))),
    LinguisticTerm("Warm", ScalarFuzzySet(universe, SShoulder(22, 30))),
))
result = scale.Fuzzify(24)
print({item.term.name: round(item.grade, 3) for item in result.memberships})
print(result.selectedTerms[0].name)
```

```text
{'Comfort': 0.667, 'Warm': 0.125}
Comfort
```

These illustrative thresholds define the model. Membership grades describe how
well the measurement fits each concept; they are not probabilities and need not
sum to one. The two terms do not cover every temperature.

![Comfort and Warm at 24 °C](https://raw.githubusercontent.com/Fuzzy-Technologies/FuzzyRoutines/v2.0.0/docs/site/content/en/assets/figures/temperature.svg)

## Use with your AI assistant

Copy this request:

> Use FuzzyRoutines 2.1.0 and its modern Python API to classify a 24 °C
> measurement. Read the version-aware quick start below, use the reviewed CI wheel if
> 2.1.0 is unavailable on PyPI, and verify Python and the installed
> package version, run the example and check Comfort = 2/3, Warm = 0.125,
> selected label = Comfort. Return the code and observed values. Explain the
> chosen thresholds and distinguish membership grades from probabilities.
> If Python execution is unavailable, label the output as expected.

[2.1 quick start](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/site/content/en/quick-start.md) ·
[Agent guide and capability map](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/site/content/en/agent-quickstart.md)

## Explore a useful scenario

These tagged 2.0 baseline guides describe scalar operations preserved in 2.1.

| Goal                              | Start here                                                                                                                               |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Classify a measurement            | [Temperature example](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/site/content/en/guides/temperature.md)        |
| Choose membership curves          | [Membership gallery](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/site/content/en/guides/membership-families.md) |
| Combine criteria, inspect results | [Worked examples](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/site/content/en/guides/index.md)                  |
| Maintain existing 1.x software    | [Compatibility and migration](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/COMPATIBILITY.md)                     |

## Explore 2.1 features

FuzzyRoutines 2.1 adds the historical Universal Fuzzy Scale factory,
linguistic encodings, traced Mamdani and Sugeno inference, explicit NumPy
batches and optional CPU neural examples. The scalar core keeps zero mandatory
runtime dependencies.

For installation checks and the new APIs, use
the [version-aware agent guide](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/site/content/en/agent-quickstart.md) and a
2.1.0 package matching the reviewed source revision.
[Release review #348](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/348)
records the reviewed release evidence.

## Learn more and contribute

- [API reference](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/api/)
- [Mathematical contracts](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/MATHEMATICAL_MODEL.md)
- [Benchmarks and their limits](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/performance/installed-batch-results.md)
- [Development and evidence rules](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/development-evidence-protocol.md)
- [Changes](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/CHANGELOG.md)

The published `/latest/` reference moves with approved releases. Use matching
tagged sources when reproducing an older version.

## License

[Apache-2.0](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/LICENSE). Preserve the license and [NOTICE](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/NOTICE).
