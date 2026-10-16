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

Install the published stable release:

```console
python -m pip install fuzzyroutines==2.0.0
```

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

> Use FuzzyRoutines 2.0.0 and its modern Python API to classify a 24 °C
> measurement. Read the tagged quick start below, verify Python and the installed
> package version, run the example and check Comfort = 2/3, Warm = 0.125,
> selected label = Comfort. Return the code and observed values. Explain the
> chosen thresholds and distinguish membership grades from probabilities.
> If Python execution is unavailable, label the output as expected.

[Stable quick start](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/site/content/en/quick-start.md) ·
[Agent guide and capability map](docs/site/content/en/agent-quickstart.md)

## Explore a useful scenario

| Goal                              | Start here                                                                                                                               |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Classify a measurement            | [Temperature example](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/site/content/en/guides/temperature.md)        |
| Choose membership curves          | [Membership gallery](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/site/content/en/guides/membership-families.md) |
| Combine criteria, inspect results | [Worked examples](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/site/content/en/guides/index.md)                  |
| Maintain existing 1.x software    | [Compatibility and migration](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/COMPATIBILITY.md)                     |

## Explore 2.1 development

The development branch adds the historical Universal Fuzzy Scale factory,
linguistic encodings, traced Mamdani and Sugeno inference, explicit NumPy
batches and optional CPU neural examples. The scalar core keeps zero mandatory
runtime dependencies.

The installation command above uses published 2.0.0. To try the new APIs, use
the [version-aware agent guide](docs/site/content/en/agent-quickstart.md) with a
reviewed wheel matching its source revision.
[Release review #348](https://github.com/Fuzzy-Technologies/FuzzyRoutines/pull/348)
tracks the current evidence and findings.

## Learn more and contribute

- [API reference](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/api/)
- [Mathematical contracts](docs/MATHEMATICAL_MODEL.md)
- [Benchmarks and their limits](docs/performance/installed-batch-results.md)
- [Development and evidence rules](docs/development-evidence-protocol.md)
- [Changes](CHANGELOG.md)

The published `/latest/` reference moves with approved releases. Use matching
tagged sources when reproducing an older version.

## License

[Apache-2.0](LICENSE). Preserve the license and [NOTICE](NOTICE).
