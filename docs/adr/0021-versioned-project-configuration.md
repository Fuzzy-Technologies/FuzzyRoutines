<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0021: Versioned fuzzy model and project configuration

## Status

Proposed for [Task #384](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/384)
under [Feature #358](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/358).
This decision defines a wire format. It adds no public loader, serializer, or
dependency.

## Context

A reusable fuzzy model must preserve the mathematics that produced its results:
the universe and its endpoints, membership parameters, term order, rule order,
and numerical policies. The same model may be reused by projects with different
labels, units displayed on plots, colors, and sample inputs. Native Python
objects can also contain arbitrary evaluators and numbers with precision
outside a portable wire format. A file must state exactly what can be rebuilt
without interpreting code or looking up configuration on the network.

## Decision

Use the [version 1 JSON Schema](../../fuzzyroutines/config-v1.schema.json), using
[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-validation),
with a separate semantic validation pass. The version is independent of the
package version. The repository file is the canonical schema and is included in installed
distributions. Its `$id` identifies the document; the loader reads its local
package resource. All
schema references are internal. A configuration cannot select its own schema.

- A `model` contains named universes, named built-in membership definitions,
  and named scales with ordered terms. It can also contain one scalar Mamdani
  or Sugeno inference definition. A scale library needs no inference definition.
- A `project` contains one or more named, inline model envelopes. It can also
  contain selected defaults, presentation, and evaluation scenarios. The
  document is self-contained.

Both envelopes declare `schemaVersion: 1`. A future optional YAML codec must
decode to the same data model and run the same validation. Project presentation
and scenarios never change the model's stored policies, numbers, or ordering.

### Model state

- A continuous universe records both endpoints and their closure flags; a
  `null` endpoint is unbounded and cannot be closed. A discrete universe lists
  a nonempty, strictly increasing sequence of coordinates. Membership support
  and numerical integration windows remain distinct from the universe
  ([ADR-0002](0002-universe-support-semantics.md)).
- A membership definition uses a closed family tag and the canonical parameter
  names of its modern constructor ([ADR-0003](0003-membership-function-contracts.md)).
  No legacy spelling aliases are accepted in the file. A scale binds each
  ordered term to one membership definition and all its terms to one universe.
  An optional scale `fuzzification` block declares the tie rule, confidence
  threshold and tie tolerance. Optional `representatives` supplies an explicit
  centroid policy and a finite closed integration window for every term;
  these are read in term order. Neither policy block is implicitly added.
- An inference definition lists ordered inputs and rules with explicit
  conjunction, disjunction, and negation policies
  ([ADR-0004](0004-operator-and-negation-contracts.md)). Its antecedents are
  `term`, `all`, `any`, or `not` nodes. Each `term` names an input and one of
  that input's terms. `all` and `any` take at least two ordered operands.
  Every rule explicitly records its product weight in `[0, 1]`.
- Mamdani stores one output variable backed by a continuous scale; a rule
  consequent selects a term from that scale. Activation and aggregation are
  independent norm choices. With no `centroid` block the evaluation returns
  the fuzzy result only; with the block the model declares its closed
  integration domain and complete quadrature policy
  ([ADR-0005](0005-numerical-defuzzification-policy.md)).
- Sugeno stores a continuous output universe. A rule can independently choose
  a zero-order `constant` or first-order `affine` consequent. An affine
  consequent stores the intercept and ordered input/coefficient pairs.
  Missing coefficients mean zero; repeated coefficients for one input fail.
  No-fire, numerical convergence, and out-of-universe evaluation behavior
  remain those of [ADR-0017](0017-scalar-fuzzy-rule-inference.md). Loading does
  not run a model, and cannot establish that every future affine evaluation
  will stay in its output universe.

The v1 membership allowlist is explicit:

| Family tag                | Parameters and constraints                   |
| ------------------------- | -------------------------------------------- |
| `hyperbolic`              | `scale > 0`, `exponent > 0`, finite `cutoff` |
| `bell`                    | `left < plateauStart <= plateauEnd`          |
| `s_shoulder`              | `left < right`                               |
| `triangle`                | `left < peak <= right`                       |
| `trapezoid`               | `left < plateauStart <= plateauEnd < right`  |
| `gaussian`                | Finite `center`, `scale > 0`                 |
| `logistic`                | `slope != 0`, finite `midpoint`              |
| `harrington_desirability` | Empty `parameters` object                    |

This allowlist covers the existing analytical families. Custom point tables
and interpolants require a separate wire representation; choosing a discrete
universe does not implicitly change an analytical family into a table.

The Universal Fuzzy Scale is stored as ordinary definitions on closed
`[0, 1]`, not as a version-dependent preset alias. The normative v1
[historical-scale example](../schemas/config-v1/fixtures/valid-historical-scale.json)
retains term order `Min`, `Low`, `Med`, `High`, `Max`; coefficients
`Hyperbolic(8, 20, 0)`, `Bell(0.17, 0.23, 0.34)`,
`Bell(0.34, 0.40, 0.60)`, `Bell(0.60, 0.66, 0.77)`,
`SShoulder(0.77, 0.95)`; and centroid windows `[0, 0.23]`, `[0.17, 0.40]`,
`[0.34, 0.66]`, `[0.60, 0.83]`, `[0.77, 1]`. Its fuzzification policy
selects the last exact maximum, with tie tolerance and minimum confidence both
zero. The positive Min tail and weak coverage remain. This preserves
[ADR-0016](0016-linguistic-encodings-and-historical-preset.md) without claiming
parity with historical sampled or cached centroids.

### IDs, references and project settings

IDs are 1–64 ASCII characters: first an ASCII letter, then letters, digits,
`_` or `-`. They are case-sensitive, with no trimming or implicit aliases.
An ID is a map key for named definitions, models, plots, and evaluations.
Terms, variables, and rules instead carry IDs in their ordered arrays. They
also carry a nonblank Unicode `name` of at most 256 code points for the
reconstructed runtime object; the spelling is preserved without Unicode
normalization. Runtime names are exact; scale term names must
additionally be distinct under Unicode case folding, as required by
`LinguisticScale`.

| Reference                                    | Target and scope                                                              |
| -------------------------------------------- | ----------------------------------------------------------------------------- |
| Scale `universe`; Sugeno `outputUniverse`    | Universe ID in the same model                                                 |
| Term `membership`                            | Membership ID in the same model                                               |
| Variable `scale`                             | Scale ID in the same model                                                    |
| Antecedent `input`, then `term`              | Input ID in the same inference definition, then term ID in that input's scale |
| Mamdani rule `consequent`                    | Term ID in the output variable's scale                                        |
| Affine coefficient `input`                   | Input ID in the same inference definition                                     |
| Representative `windows` keys                | Term IDs in that scale, with exactly one window per term                      |
| `presentation.units` keys                    | Project model IDs, then local universe IDs                                    |
| Plot `model`, `scale`, and `termColors` keys | Project model ID, then local scale ID, then term IDs in that scale            |
| Evaluation `model` and `inputs` keys         | Project model ID, then exactly the selected inference definition's input IDs  |
| Project `defaults` fields                    | IDs in `models`, `presentation.plots`, and `evaluations`, respectively        |

IDs may repeat across distinct namespaces. A term ID is unique within its
scale; variable IDs are unique across an inference definition's inputs and
Mamdani output; rule IDs are unique within their rule array. Input names and
rule names are separately unique as in the runtime. Binding to runtime objects
translates IDs to the corresponding names; it never uses a display label as a
substitute for a missing ID. Forward references are valid. The fixed reference
graph has no recursive object references: only antecedents can nest, inline.

Projects may declare display units per universe and a plot title, axis label,
and opaque `#RRGGBB` term colors. Units are labels, not conversion rules. Plot
order follows the chosen scale's terms; the color map is an optional partial
override. A scenario requires a model with inference, one finite coordinate
within each declared input universe, and a flag for showing traces. No file
is evaluated on load. With no explicit default, a consumer
must select an entry even for a singleton project. If default plot or evaluation
IDs are specified, they must select the same model as `defaults.model`.
Missing or conflicting defaults fail when specified; a reader never guesses a
target. Version 1 has no local or remote file references, output filenames,
include or inheritance mechanism. The caller explicitly chooses any file to
open or write outside the document.

### Validation, errors and deterministic output

Validation occurs before any model construction is exposed to callers:

1. Parse one bounded UTF-8 document. Reject duplicate keys at every depth,
   unpaired Unicode surrogates, non-string keys, non-JSON scalars, and limits
   exceeded. V1 limits the encoded document to 1,048,576 bytes, parsed nesting
   to 96 containers (root counts as one), parsed size to 65,536 nodes (each
   object, array, scalar value, and object key counts as one), and antecedent
   depth to 64 nodes along any root-to-leaf path. Bound the parser as it reads;
   do not rely on a later schema rejection to constrain allocations.
2. Dispatch using the exact envelope kind and integral schema version. An
   unknown kind or version fails explicitly, including for inline models.
   Validate the structure against the selected locally supplied schema. Fields
   are closed; unknown names, kinds, families, or parameters fail. IDs and
   names use separate syntactic rules.
3. Validate semantic constraints. Reject all-whitespace labels, duplicate IDs or
   runtime names in their declared namespaces, and unknown or wrong-scope
   references. Validate all ordered geometry, integration domains, term
   window coverage, universe types, constants in the declared output
   universe, and scenario inputs/default relationships. Integration windows
   require a continuous universe and both bounds must be members. Real
   comparisons occur after conversion to the v1 numerical representation.
4. Only then use explicit allowlisted constructors. No evaluator, plotting
   routine, or scenario runs during validation, migration, or loading.

A future codec must report an error category and an
[RFC 6901 JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901) to the offending
field, even when the input is YAML. Use an empty pointer for a document-wide
error. Distinguish malformed/unsafe documents, unsupported kind/version,
invalid shape, duplicate ID/name, unresolved reference, invalid value or
relationship, and unsupported source values on export. For a missing reference
report the location that supplied it, for example
`/inference/rules/0/antecedent/input` plus the input namespace and ID. A
missing required field or mismatched type is a shape error. Duplicate IDs
in ordered arrays point at the second occurrence. A default that names an
existing entry for the wrong model is an invalid relationship. Diagnostics
must not return a partial model or execute file data. If only one failure is
reported, use validation-phase order; within semantic validation visit object
keys in ASCII order and arrays in declared order. Schema-engine wording is
not a public contract.

V1 real-valued fields use finite IEEE 754 binary64. A reader converts valid
decimal number tokens by rounding to nearest with ties to even, retaining
signed zero. It rejects overflow, nonzero values that round to zero, NaN,
infinities, booleans in numeric slots, and numeric strings. Schema bounds
apply to the decoded values; for example structural `type: number` alone
cannot detect an underflowed token. Integer version/depth fields retain their
exact integral value and depth is restricted to `[0, 2^53-1]`. A writer must
reject source numbers whose value cannot be represented in the field without
loss, rather than round a higher precision model silently.

JSON exports use UTF-8 without a BOM, LF, stable ASCII key sorting, and the
codec's deterministic round-trip decimal representation for binary64
(including negative zero). No float or other value is emitted as a string to
work around schema constraints. Maps have no semantic order. Preserve array
order for terms, inputs, rules, operands and affine coefficients. Validate
ordered coordinates instead of sorting them. Identical wire data emitted by
the same codec must produce identical bytes; JSON/YAML or different codec
implementations need semantic equivalence, not identical formatting. Runtime
round-trips compare model structure, evaluation and trace order on supported
inputs under the existing numerical policy, not Python object identity.

No implicit version upgrades or downgrades are allowed. An explicit future
migration must validate the source version, apply a documented deterministic
data-only transform that preserves mathematical semantics (or report why it
cannot), and validate the resulting target version before use or save. The
original file is never modified by a read. There is no migration path from
pickled objects or guessed unversioned documents.

JSON is data only. The future YAML codec must accept one document in the JSON
data model, with string keys, and must reject duplicate keys, tags, anchors,
aliases, merge keys, and automatic scalar conversions outside that model.
Neither format supports Python expressions, pickle, callable import paths,
dynamic plugin names, implicit network or filesystem access, or environment
substitution. Legacy adapters, closures, arbitrary callable objects,
subclasses with custom evaluators, and unlisted families are unsupported for
export; report the source field and tell the caller to choose a supported
explicit family or keep the evaluator in code. Do not infer trust from object
attributes or approximate callbacks through sampling.

## Alternatives

- Python object or callable serialization would persist implementation detail
  and could run code. Use a data allowlist instead.
- Flattening presentation into mathematical state would let a plot edit affect
  round-trip semantics. Keep separate sections.
- A project manifest with paths or remote imports would need a resolution and
  trust model and would no longer be self-contained. Keep inline models in v1.
- JSON Schema alone cannot enforce typed reference targets, per-ID uniqueness
  in object arrays, ordered geometry, and numeric parser limits. Validate
  these independently before reconstruction.

## Output

Versioned offline schema and [isolated design fixtures](../schemas/config-v1/README.md),
with [Russian](../schemas/config-v1/README.ru.md) and
[Simplified Chinese](../schemas/config-v1/README.zh-CN.md) guides. The JSON codec in
[#385](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/385), optional
YAML codec in [#386](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/386),
and project handling in [#387](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/387)
will exercise the structural and semantic stages and verify end-to-end
round-trips. This proposal leaves the existing Python APIs and preset unchanged.
