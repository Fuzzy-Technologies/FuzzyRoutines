<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0025: Fuzzy calculator command contract

- Status: Proposed for 2.2
- Date: 2026-11-06
- Task: [#389](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/389)
- Feature: [#359](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/359)
- Builds on: [ADR-0016](0016-linguistic-encodings-and-historical-preset.md), [ADR-0017](0017-scalar-fuzzy-rule-inference.md), and [ADR-0021](0021-versioned-project-configuration.md)

## Context

People and automation need a small installed calculator with stable results,
visible choices, and actionable errors. The existing scalar API owns fuzzy
semantics. A CLI invocation selects data, binds inputs and renders results
using the same model and policies.

## Decision

Install the `fuzzyroutines` entry point. Select a local v1 model or project
envelope with the required `--project PATH` on every operation. Dispatch
`.json` to the JSON codec and `.yaml` or `.yml` to the optional safe YAML
codec when installed. Unsupported suffixes and unavailable capabilities fail
explicitly. Relative paths resolve against the caller's working directory.
Validation reads only the specified document. There is no expression parser,
plugin resolution, shell expansion by the calculator, or implicit resource
loading.

The syntax below puts options after the command. Square brackets indicate
optional arguments, and an ellipsis indicates a repeatable option.

```text
fuzzyroutines membership --project PATH [--model NAME] --scale ID --term ID --x NUMBER
fuzzyroutines fuzzify --project PATH [--model NAME] --scale ID --x NUMBER
fuzzyroutines infer --project PATH [--model NAME] [--evaluation ID] [--input ID=NUMBER ...] [--term-input ID=TERM ... --encoding representative-centroid] [--explain]
fuzzyroutines validate --project PATH
fuzzyroutines plot --project PATH [--model NAME] [--plot ID | --scale ID] --output PATH [--overwrite]
```

`NAME` and `ID` select exact, case-sensitive configuration IDs. A standalone
model needs no selector and rejects `--model`, `--evaluation` and `--plot`.
A project resolves the effective model in this order:

1. An explicit `--model`.
2. The model referenced by an explicit `--evaluation` or `--plot`.
3. The project's declared `defaults.model`.

An explicit model and a named scenario or preset must agree when combined.
An absent selection fails even for a singleton project. An unknown explicit
ID fails without falling back. An explicit `--scale` and an explicit
`--plot` are mutually exclusive.

- **Membership** evaluates the selected term at the supplied coordinate. It
  returns its ID, coordinate and scalar grade.
- **Fuzzify** classifies the coordinate under the scale's declared policy.
  If omitted, use the scalar API's default. Return every term grade in scale
  order, confidence, tied and selected IDs, and match status. A no-match
  classification is a successful result with empty selections.
- **Infer** executes the selected model's existing scalar inference. An
  explicit `--evaluation` supplies the base inputs. Otherwise, explicit input
  options form the entire binding, or, if none are supplied, use the project's
  declared `defaults.evaluation` when it applies to the selected model.
  A mismatched default is inapplicable. Explicit input options override a
  named scenario per ID. An unknown ID, a duplicate ID across input options,
  or any missing final input fails. `--explain` enables the trace. In its
  absence, use the selected scenario's trace flag or false without a scenario.
- **Validate** checks the entire envelope, including unused models, and
  returns its kind and schema version on success. It never runs inference
  or renders a plot. Other commands also validate the entire envelope before
  selecting their target.
- **Plot** uses the explicitly selected preset or scale. When neither is
  supplied, use the declared default plot if it applies to the selected
  model. A plot without a preset or scale fails. Preset title, units and
  colors affect presentation only. Require an explicit output path with
  `.png`, `.jpg`, `.jpeg`, or `.svg` suffix. A pre-existing output fails
  unless `--overwrite` is supplied. The plot task owns format and sampling
  policies. No rendering occurs when support is unavailable.

Numeric tokens use the JSON number grammar and ADR-0021's finite binary64
conversion policy. Each resulting input coordinate must belong to its
declared universe. `--term-input` requires the explicit
`--encoding representative-centroid` policy and the input scale's declared
representative windows and centroid policy. Select a term by ID and pass its
resolved exact label to the ADR-0016 scalar encoding. The resulting coordinate
goes through the same input validation as a numeric coordinate. Missing
windows, unknown terms, undefined centroids, and an encoding flag with no
term inputs fail. A term is an identifier in a configured scale. An argument
like `--input 'risk=Low + Min'` is invalid. There is no term arithmetic or
implicit mapping from labels to numbers.

### Streams and exit status

Machine operations emit one UTF-8 JSON object followed by LF. A success object
on stdout has `resultVersion: 1`, `command`, and `result`. Within
`result`, use the command-specific fields below. Keys use ASCII ordering and
arrays retain declaration order. Numbers are finite. Locale, color, and
terminal settings cannot change machine output. An error leaves stdout empty
and emits one object on stderr with `resultVersion: 1` and `error`. The
error contains a stable `category`, diagnostic `message`, and, for codec
errors, the codec's `pointer` and finer `detailCategory`. The pointer is
empty for an envelope-level error. Diagnostic wording is not stable. No
traceback is part of the machine contract. Help and version emit plain text
on stdout and return zero.

- `membership` returns `scale`, `term`, `coordinate`, and `grade`.
- `fuzzify` returns `scale`, `coordinate`, `memberships` (ordered
  `{term, grade}` records), `confidence`, `tiedTerms`, `selectedTerms`,
  and `match`.
- `infer` returns `kind`, `method` and `value`. For Mamdani without a
  centroid request, `value` is null and `method` is `fuzzy-set`. The
  aggregate evaluator remains in memory and is not serialized. If enabled,
  `trace` has `inputGrades` (ordered `{input, term, grade}` records) and
  `rules` (ordered records with `rule` ID, `antecedentGrade`, `weight` and
  `firingStrength`). A Sugeno rule record also carries `consequentValue`,
  `normalizedStrength`, and `contribution`. No trace key is emitted when off.
- `validate` returns `kind` and `schemaVersion`.
- `plot` returns `output` (the supplied path) and `format` (one of
  `png`, `jpeg`, or `svg`). The file is the only plot payload.

Exit codes and error categories are stable:

- `0` for success.
- `2`, `usage`, for invalid arguments, number syntax or conversion, and
  invalid or incomplete target or input bindings.
- `3`, `configuration`, for malformed, unsupported or semantically
  invalid envelopes, preserving the codec diagnostic.
- `4`, `evaluation`, for domain violations, no firing, undefined
  representative or centroid results, numerical failures, and renderer errors
  on otherwise valid requests.
- `5`, `io`, for file access, output conflicts and write failures.
- `6`, `capability`, for missing optional codec or renderer support.

Process requests in command syntax, file access and validation, selection and
binding, then evaluation or rendering order. Report the first failure. No
failed command emits a partial successful JSON result.

### Acceptance cases

The commands below are proposed. Run the JSON cases against the tracked
[project fixture](../schemas/config-v1/fixtures/valid-project.json) from
the repository root. The YAML invocation assumes an equivalent v1 project
file supplied by the caller once the optional codec is installed.

```sh
fuzzyroutines validate --project docs/schemas/config-v1/fixtures/valid-project.json
fuzzyroutines membership --project docs/schemas/config-v1/fixtures/valid-project.json --scale risk --term high --x 0.25
fuzzyroutines fuzzify --project docs/schemas/config-v1/fixtures/valid-project.json --model weighted --scale risk --x 0.25
fuzzyroutines infer --project docs/schemas/config-v1/fixtures/valid-project.json --evaluation quarter --explain
fuzzyroutines infer --project model.yaml --model weighted --input risk=0.8 --explain
fuzzyroutines plot --project docs/schemas/config-v1/fixtures/valid-project.json --plot risk --output risk.svg
```

Validation returns project v1. Membership and fuzzification return the
fixture's high grade of `0.125` at `0.25`. The quarter evaluation fires
`base` and `increase` at `0.875` and `0.125`, yielding a Sugeno value
of `0.296875`. With explicit risk `0.8`, the
equivalent project yields approximately `0.848`. An explicit
`--model centroid --evaluation quarter` fails with usage exit `2`. The
fixture with [an unresolved reference](../schemas/config-v1/fixtures/invalid-semantic-reference.json)
fails with configuration exit `3` and the underlying reference pointer.
Re-running the plot command against the same path without `--overwrite`
fails with I/O exit `5`.

## Consequences

The installed evaluation and model inspection implementation belongs to
[#390](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/390), with
the JSON codec in [#385](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/385)
and renderer in [#394](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/394).
When those capabilities ship, their executable examples and adaptive EN, RU,
and zh-CN guides must follow [ADR-0010](0010-api-documentation-architecture.md)
and [ADR-0011](0011-multilingual-documentation-pipeline.md). This design adds
no executable command or dependency.
