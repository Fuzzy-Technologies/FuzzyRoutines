<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Agent quick start

Give an assistant this page when you want it to install FuzzyRoutines, explain
its capabilities, calculate memberships or draw a reproducible graph. The
assistant needs a Python execution environment; a chat-only assistant can read
and explain the example, but cannot honestly report that it executed it.
No local PC, Docker, GPU, model provider or agent framework is required.

## Copyable request

> Read https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/en/agent-quickstart/ . Check Python first, install exactly FuzzyRoutines 2.0.0, construct the historical Universal Fuzzy Scale using its supported modern API, and run the scale and illustrative risk recipes. Return the package version, inputs, five membership grades, selected label or no match, and numerical checks. If plotting is available, produce a headless graph. Explain the weak coverage near 0.17 and why membership grades are not probabilities. If execution is unavailable, say so and provide the commands without claiming results.

## Version and capability map

This recipe targets the **published 2.0.0** API on CPython **3.13 or 3.14**.
The `/latest/` documentation route moves; the exact package pin and the JSON
`environment` record identify what was actually run. The standalone recipe
works against an installed wheel and imports no repository modules.

| Capability                            | Published 2.0.0 entry point                                                                 | Example                                                                     |
| ------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Sets and memberships                  | `ScalarFuzzySet`, `Triangle`, `Bell`, `Hyperbolic`, `SShoulder`                             | [Membership gallery](guides/membership-families.md)                         |
| Linguistic classification             | `LinguisticScale.Fuzzify`, `FuzzificationPolicy`                                            | [Historical scale](guides/universal-fuzzy-scale.md)                         |
| Fuzzy logic primitives                | `TNormPolicy`, `SNormPolicy`, `NegationPolicy`, set operations                              | [Operators](guides/operators.md)                                            |
| Cuts and numeric output               | `AlphaCut`, `SampleAlphaCut`, `Centroid`                                                    | [Alpha cuts](guides/alpha-cuts.md), [centroid](guides/centroid.md)          |
| Rule inference and neural integration | Planned for 2.1; not part of the published 2.0.0 API                                        | [2.1 plan](https://github.com/Fuzzy-Technologies/FuzzyRoutines/milestone/8) |
| Optional NumPy batches                | Planned for 2.1; 2.0.0 uses the dependency-free scalar core                                 | [2.1 plan](https://github.com/Fuzzy-Technologies/FuzzyRoutines/milestone/8) |

The [API reference](api/index.md) and [worked scenarios](guides/index.md) are
authoritative. Do not guess names from a future roadmap or historical package.

## Run without a checkout

In a fresh environment, run these commands in order. The preflight stops before
installation on unsupported Python. The recipe then requires the exact installed
version, so an old `1.0.3` cannot masquerade as the modern API.

```bash
python -c "import platform, sys; sys.exit(0 if platform.python_implementation() == 'CPython' and sys.version_info[:2] in ((3, 13), (3, 14)) else 'Use CPython 3.13 or 3.14; do not install on 3.12.')"
python -m pip install fuzzyroutines==2.0.0
curl -fLo agent_recipe.py https://fuzzy-technologies.github.io/FuzzyRoutines/recipes/agent_recipe.py
python -I agent_recipe.py --expect-version 2.0.0 --output scale.json > scale.stdout.json
python -I agent_recipe.py --expect-version 2.0.0 --scenario risk --output risk.json > risk.stdout.json
python -I agent_recipe.py --expect-version 2.0.0 --scenario risk --value 17 --output weak.json > weak.stdout.json
```

The first run evaluates `x=0.2`: **Low ≈ 0.5**, with the original small positive
Min tail; the selected label is **Low**. The risk example declares an illustrative
0–100 score and divides it by 100: **75 → 0.75 → High = 1**. At **17 → 0.17**,
the largest membership is only about **0.00212959**, so the risk threshold `0.1`
produces **no match**, not a confident Min decision.

Each command writes valid JSON to stdout and, with `--output`, the same JSON to
a file. The evidence contains package/Python versions, input normalization,
original coefficients, centroid-window provenance, selection policy and checks
against independent piecewise formulas with absolute tolerance `1e-12` and zero
relative tolerance. Failure returns exit code 2 and diagnostics on stderr;
`--help` works before installing the package. These finite reference checks are
regression evidence, not proof for every real input.

The risk score is supplied by the caller; the library does not infer incident
probabilities or choose a response. Define and validate your own normalization.
Values outside the declared range are rejected, never silently clamped. Grades
need not sum to one. The policy selects the **last exact maximum**; floating-point
near ties are not exact ties. A maximum **equal to** the threshold is also no match.

## Draw and inspect the result

Plotting is optional and has a separate pinned dependency file. It uses a
headless renderer; replace `risk.svg` with `risk.png` for PNG. The graph combines
the five historical curves with a membership bar chart and the selected result.
The JSON adds the figure hash and Matplotlib version. Repeated runs with the same
pinned toolchain and inputs produce identical image bytes.

```bash
curl -fLo requirements-plots.txt https://fuzzy-technologies.github.io/FuzzyRoutines/recipes/requirements-plots.txt
python -m pip install -r requirements-plots.txt
python -I agent_recipe.py --expect-version 2.0.0 --scenario risk --value 17 --plot risk.svg > plot.stdout.json
```

[![Historical curves beside the five memberships at 0.17; all grades fall below the 0.1 decision threshold.](assets/figures/agent-risk.svg)](assets/figures/agent-risk.svg)

For a development wheel, install that exact artifact and change `--expect-version`
to its version (for example `2.1.0.dev0`). This is an explicit candidate check,
not an instruction to install an unpublished release from PyPI. Keep the JSON
and image together when reporting a result.
