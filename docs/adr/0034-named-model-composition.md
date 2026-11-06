<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0034: Compose independent scalar models with named outputs

## Status

Proposed for [Task #426](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/426)
under [Feature #372](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/372).
This checkpoint defines the in-memory contract. Runtime implementation and
its API reference and localized examples remain open.

## Context

[ADR-0017](0017-scalar-fuzzy-rule-inference.md) gives each scalar model one
output. An application can use the same observation to compute several
independent results, such as a Mamdani response set and a Sugeno score. It
needs to name and inspect both results without altering rule firing,
centroid policy, trace structure, or the historical scale in
[ADR-0016](0016-linguistic-encodings-and-historical-preset.md).

## Decision

A composition is an immutable, nonempty ordered tuple of output bindings
and an explicitly selected failure policy. Each binding contains an
external output ID, a built-in scalar Mamdani or Sugeno model, and an
ordered tuple of pairs from the model's exact input names to external input
IDs. Bindings retain scalar models and their callbacks by reference.
Callback ownership and purity follow the scalar contract.

- External input and output IDs use the case-sensitive ASCII ID grammar in
  [ADR-0021](0021-versioned-project-configuration.md). The namespaces are
  separate. An input and an output may use the same ID without any data flow
  between them. Duplicate output IDs fail at construction.
- Each binding names every scalar input exactly once in model declaration
  order. Unknown, missing, or repeated scalar input names fail at
  construction. A repeated external ID across bindings or within one
  binding explicitly shares one coordinate. Equal scalar input names
  alone do not share coordinates.
- The required external input IDs are the union of the declared binding
  targets, ordered by their first appearance. Evaluation snapshots the
  caller's mapping, rejects missing and extra keys and validates finite real
  coordinates before calling any model. It passes each original coordinate
  to the designated model inputs without conversion or clipping. Each
  model applies its own universe checks.
- A Mamdani binding may provide an explicit integration domain and centroid
  policy. Without a domain it returns its existing aggregate and trace
  with no centroid. A centroid policy without a domain and centroid
  options on Sugeno bindings fail at construction. Successful outputs
  retain the original scalar result and trace types.
- Evaluate each binding once in output declaration order. The result is an
  immutable ordered tuple of records keyed by output ID. Input map
  insertion order does not affect results. A repeated model reference
  is evaluated independently for each binding with its own inputs and
  options.

### Failure policy

Construction and input prevalidation failures reject the whole request under
either policy. For a scalar evaluation failure, select one of two explicit
policies:

- **Fail fast** stops at the first failed output, identifies its output ID
  and preserves the scalar error as its cause. It returns no partial result.
  Earlier calls may already have evaluated callbacks.
- **Per output** records an output-specific failure and continues in
  declaration order. A failure record contains a stable category and a
  diagnostic message. It contains no synthetic value or trace. Preserve
  distinctions among domain violations, undefined results, convergence
  failures and other numerical errors. Unexpected exceptions propagate
  under either policy, including arbitrary callback exceptions outside
  the documented scalar error types.

A scalar method and its trace remain observable in each successful result.
Sharing an observation across two components does not require their input
universes to agree. A coordinate accepted by one model may fail another
model's domain check under the chosen policy.

### Resource and format boundaries

Reject more than 64 output bindings, 256 distinct external inputs, or 4,096
input binding pairs at construction. These caps bound orchestration size.
Scalar evaluation and callback costs continue to follow the component
contracts. The wrapper retains no cache and adds no dependencies.

Components are scalar models. A component cannot be a composition, consume
another output, or reference itself through a binding. This rules out
binding cycles by construction. The v1 project schema continues to store
independent models and single-model evaluations. A caller can assemble the
composition explicitly from loaded models in memory. Wire representation
of compositions requires a separate ADR and versioning decision.

## Scalar parity reference

[The existing inference example](../../examples/inference.py) supplies
the two scalar components for this reference. The explicit binding is
`riskScore` to `risk` in both components. The expected output order is
`response` followed by `score`. At $x=1/4$, ADR-0017 derives the independent
Mamdani centroid $37/96$ and zero-order Sugeno result $7/20$. Both components
must retain firing strengths $(3/4,1/4)$ and their own method and trace.

```python
from math import isclose as IsClose

from examples.inference import BuildModels
from fuzzyroutines import IntegrationDomain

mamdani, sugeno, _ = BuildModels()
observation = {"riskScore": 0.25}
response = mamdani.Evaluate({"risk": observation["riskScore"]}, IntegrationDomain(0, 1))
score = sugeno.Evaluate({"risk": observation["riskScore"]})
outputs = (("response", response), ("score", score))

assert tuple(name for name, _ in outputs) == ("response", "score"), "Preserve declared output order."
assert response.value is not None and IsClose(response.value, 37 / 96, rel_tol=0, abs_tol=1e-12), "Match the analytical centroid within the scalar integration tolerance."
assert IsClose(score.value, 7 / 20, rel_tol=0, abs_tol=1e-15), "Match the hand-calculated weighted result within binary64 round-off."
for _, result in outputs:
    assert tuple(rule.firingStrength for rule in result.rules) == (0.75, 0.25), "Keep component rule order and exact firing strengths."
```

The reference runs directly from the checkout using the current scalar API.
An implementation must compare each composed result and trace against its
direct scalar call, including a Mamdani binding without a centroid. Tests must
also cover ordered outputs with different input-map orders, duplicate output
IDs, exact case, explicit sharing and independent bindings, and missing or
extra inputs with callback counters proving prevalidation. Exercise both
failure policies with a no-fire or domain failure followed by a successful
component, and reject each resource limit at its first excluded size.
