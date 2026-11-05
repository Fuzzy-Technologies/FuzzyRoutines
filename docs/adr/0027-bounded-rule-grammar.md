<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0027: Bounded readable rule grammar

- Status: Proposed for 2.2
- Date: 2026-11-06
- Task: [#414](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/414)
- Feature: [#367](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/367)
- Builds on: [ADR-0017](0017-scalar-fuzzy-rule-inference.md) and [ADR-0021](0021-versioned-project-configuration.md)

## Context

A readable rule should expose its antecedent, weight and output without
requiring a project author to write a JSON tree. The model still owns the
variables, membership functions, policies, universe and scalar evaluation.
A rule string is a bounded authoring input to one already selected model.

## Decision

Parse one complete rule from UTF-8 into a typed, inert draft. Resolve that
draft against a caller-supplied model definition before constructing a scalar
rule or exporting its data. The context fixes the inference kind and supplies
the v1 IDs and corresponding exact runtime names for inputs and terms.
The parser neither constructs a complete model nor executes inference.

~~~text
rule        = "RULE" id string "IF" disjunction "THEN" consequent "WEIGHT" number
disjunction = conjunction { "OR" conjunction }
conjunction = negation { "AND" negation }
negation    = "NOT" negation | "(" disjunction ")" | string "IS" string
consequent  = "TERM" string | "CONSTANT" number | affine
affine      = "AFFINE" "(" number { "," string ":" number } ")"
~~~

- `id` is an ADR-0021 ID and identifies the rule in its inference definition.
  The first `string` in a rule is its nonblank display name. All other strings
  refer to exact runtime names. Resolve them to v1 IDs using the supplied
  context. Both the rule ID and rule name must be unique when inserting into
  a model.
- A `string` is a JSON string token. Double quotes and backslashes use JSON
  escapes, and Unicode escapes must decode to Unicode scalar values. Reject
  unescaped control characters, lone surrogates, all-whitespace strings and
  decoded names longer than 256 code points. Preserve spelling and compare
  case-sensitively without trimming, normalization or label aliases.
- Keywords are uppercase and recognized only as complete tokens in their
  grammatical positions. A rule ID may have the spelling of a keyword.
  ASCII space, tab, CR and LF separate tokens outside strings. The lexer
  reads complete tokens, so `NOTHING` cannot match `NOT`. Adjacent word and
  number tokens require a separator. Comments and trailing content fail.
- `number` is one JSON number token under the ADR-0021 finite binary64
  policy. It retains signed zero and rejects overflow and nonzero underflow.
  Rule weights are required and must be in the closed interval `[0, 1]`.
  The weight multiplies the antecedent grade under ADR-0017.
- `NOT` binds more tightly than `AND`, which binds more tightly than `OR`.
  Consecutive unparenthesized operands of the same operator become one
  ordered `AllOf` or `AnyOf` node. An explicitly grouped node keeps its own
  children, even under another node of the same kind. For example,
  `A AND (B AND C)` and `A AND B AND C` have different trees, where
  `A`, `B` and `C` stand for complete predicates. No algebraic rewrites,
  sorting, deduplication or short-circuiting are introduced.
- The left string of `IS` names an input. The right string names one term
  of that input's scale. `TERM` names one term of the Mamdani output scale.
  `CONSTANT` and `AFFINE` are Sugeno-only. `AFFINE` records an intercept and
  ordered pairs of input name and coefficient. Repeated names fail, omitted
  coefficients contribute zero, and an explicit zero coefficient stays in
  the record. `AFFINE(0)` remains an affine consequent. The rule kind must
  agree with the selected model, and constant output values must belong to
  its output universe. An affine rule's evaluated output remains subject
  to the existing scalar checks.
- A rule accepts at most 65,536 encoded bytes and 4,096 lexical tokens
  before building runtime objects. Bound recursive nesting to 64 pending
  groups or negations and the emitted antecedent to 64 nodes on any
  root-to-leaf path. Reject on crossing any limit. Use distinct error
  categories for malformed input, exceeded limits, unresolved bindings
  and invalid rule semantics. Report a zero-based UTF-8 byte offset for
  the start of the offending token, or the byte length at end of input.
  Publish neither a partial rule nor an updated model on failure.

No natural-language hedges, label arithmetic, implicit unit conversion,
quoted-expression evaluation, user-defined operators, imports, callbacks,
or resource lookups are part of the grammar. The same model retains its
existing operator choices and historical scale coefficients.

## Canonical text and round trip

Emit one rule with one ASCII space between words, no space inside a
parenthesized operand at its delimiters, and one space after commas and
colons in `AFFINE`. End with LF. Use literal UTF-8 for printable Unicode,
JSON escapes for quotes, backslashes and controls, and deterministic
shortest round-tripping binary64 decimal tokens, including `-0` for
negative zero. Parenthesize a child operator of lower precedence and a
child operator of the same n-ary kind. Preserve operand and coefficient
order. Insignificant user whitespace and escape spellings are not retained.

In the same model context, parsing canonical text reproduces the typed
tree and v1 rule fields, including coefficient order, rule name, rule ID
and signed zero. The mapping is only defined for the supported v1 rule
subset with an unambiguous reverse lookup for every reference. Reject
unrepresentable inputs instead of guessing an ID or narrowing a number.

## Acceptance cases

For a model with the input names `risk`, `sensor` and `load` and their
shown terms, valid Mamdani, constant Sugeno and affine Sugeno rules are:

~~~text
RULE alarm "Alarm" IF "risk" IS "High" THEN TERM "Urgent" WEIGHT 1
RULE hold "Hold" IF "sensor" IS "Level \"A\"" THEN CONSTANT 0.25 WEIGHT 0.5
RULE adjust "Adjust" IF NOT "risk" IS "Low" AND ("sensor" IS "Stable" OR "load" IS "High") THEN AFFINE(0.25, "load": -0.5, "risk": 0.75) WEIGHT 0.8
~~~

The last rule lowers to an `AllOf` containing a `NotCondition` on
`risk` and an ordered `AnyOf` on `sensor` and `load`. Its affine value
at load `0.25` and risk `0.5` is exactly `0.5`. If the antecedent grade
is `0.5`, the weighted firing is `0.4` under the binary64 scalar policy.
These values require neither a linguistic encoding nor a unit conversion.

Reject an unknown term such as `"risk" IS "HIGH"` when only `"High"` is
declared. Reject a repeated coefficient in `AFFINE(0, "risk": 1, "risk": 2)`,
a wrong-kind consequent, `WEIGHT 1.01`, `WEIGHT 1e-999`, and
`"risk" IS "Low" + "Min"`. Reparse canonical output and check the full
ordered AST and v1 rule fields. Use a nested same-operator case and a
negative-zero coefficient as separate regression fixtures.

## Output

Task [#415](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/415)
owns parser and serializer implementation, deterministic negative cases
and adaptive EN/RU/zh-CN usage guides under
[ADR-0010](0010-api-documentation-architecture.md) and
[ADR-0011](0011-multilingual-documentation-pipeline.md).
