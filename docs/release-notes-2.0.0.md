<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines 2.0.0 — Explicit mathematics. Historical continuity

![FuzzyRoutines and Alice](https://raw.githubusercontent.com/Fuzzy-Technologies/FuzzyRoutines/202c58f16bf072b98765adaf1fa05f94c98f6cf1/docs/site/content/en/assets/brand/fuzzyroutines-alice.png)

FuzzyRoutines 2.0 brings a typed scalar API, explicit mathematical domains and
controlled numerical methods to the library, while preserving the protected
historical interface used by existing projects.

## Highlights

- Modern membership factories, explicit universes, scalar fuzzy sets,
  operators, alpha cuts, fuzzification and centroid evaluation.
- The historical **Universal Fuzzy Scale**, explained and reconstructed with
  the modern API, with graphs and examples of interpreting cybersecurity and
  risk levels. Membership grades express compatibility with a level; they
  are not probabilities or calibrated risk estimates.
- Complete English, Russian and Simplified Chinese documentation, nine worked
  scenarios and eleven reproducible scientific figures.
- A refreshed project site and API reference with corporate typography,
  MathJax formulas, copyable examples and an accessible in-page image viewer.
- Reproducible wheel/source builds, installed-package checks and protected
  PyPI Trusted Publishing with post-publication hash and installation checks.

## Install

Use CPython **3.13 or 3.14**:

```console
python -m pip install fuzzyroutines==2.0.0
```

Start with the [quick start](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/quick-start/)
or the [Universal Fuzzy Scale guide](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/guides/universal-fuzzy-scale/).
The API reference is also available in
[Russian](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/ru/)
and [Simplified Chinese](https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/zh-CN/).

## Upgrading from 1.0.3

Historical calls remain available through `fuzzyroutines.FuzzyRoutines`;
the package root exposes the modern API. Version 2.0 introduces stricter
input validation, corrected numerical behavior, explicit helper imports and
the CPython 3.13 runtime floor. Project-owned code is now Apache-2.0; the
historical 1.0.3 baseline retains its original license.

Read the [migration guide](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/docs/migration/1.0.3-to-2.0.0.md)
and [full changelog](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/v2.0.0/CHANGELOG.md)
before upgrading an existing application.
