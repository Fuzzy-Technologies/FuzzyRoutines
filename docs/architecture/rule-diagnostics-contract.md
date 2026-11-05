<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Structural rule diagnostics

Status: Proposed for [Task #408](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/408).

## Context

[ADR-0017](../adr/0017-scalar-fuzzy-rule-inference.md) validates input and
output references when constructing a model. Authors need to inspect all
invalid references in an ordered rule draft before that step. Valid rules
can also have patterns that deserve a closer look.

## Decision

Inspect the existing typed rule records against the input variables and
output declaration. Return immutable diagnostics in declaration order,
with stable codes and zero-based rule indices. Do not run membership
callbacks, inference, or numerical sampling. Keep model constructors and
evaluation independent of diagnostics.

| Observation                               | Severity | Rationale                             |
| ----------------------------------------- | -------- | ------------------------------------- |
| Unknown input, input term, or output term | Error    | Model bindings cannot resolve it      |
| Unknown affine coefficient input         | Error    | The coefficient cannot bind           |
| Repeated rule name                       | Error    | The constructor requires unique names |
| Zero weight                              | Warning  | The rule cannot fire                  |
| Exact active rule repeated               | Warning  | The repeat can change aggregation     |
| Same active antecedent, different output | Warning  | The rules may intentionally blend     |

Report references in expression traversal order, retaining the first
occurrence of a repeated invalid reference per rule. Check even zero-weight
rules because scalar models validate all declared references. Skip pairwise
findings for rules with invalid references or zero weight.

Use ordered AST equality for antecedents. Do not reorder operands, simplify
expressions, or infer equivalence from different ASTs. An exact active
duplicate has the same antecedent, consequent record, and weight. A potential
conflict requires the same antecedent and different declared output terms or
different Sugeno coefficient maps or intercepts. Ignore explicit zero affine
coefficients when comparing outputs for conflict. Weight differences alone
do not constitute a conflict. Report the earliest earlier matching rule for
each finding on a later rule.

For example, given an input `risk` with terms `low` and `high`, a
reference to `risk.missing` is an error. Two unit-weight rules with
`risk.high` and the same consequence trigger a duplicate warning. Another
rule with the same antecedent and a different consequence triggers a
conflict warning. A conjunction of `risk.high` and another term does not
trigger a conflict against the standalone `risk.high` rule. Coverage and
overlap require a separate analysis.

## Output

An additive, dependency-free diagnostics API with hand-checkable tests and
localized usage guidance. This contract leaves the 2.x scalar inference and
historical Universal Fuzzy Scale unchanged.
