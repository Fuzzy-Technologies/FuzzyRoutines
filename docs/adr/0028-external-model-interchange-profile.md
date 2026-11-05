<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0028 External model interchange profile

- Status: Proposed checkpoint for 2.2
- Date: 2026-11-06
- Task: [#424](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/424)
- Feature: [#371](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/371)
- Builds on: [ADR-0016](0016-linguistic-encodings-and-historical-preset.md), [ADR-0017](0017-scalar-fuzzy-rule-inference.md), and [ADR-0021](0021-versioned-project-configuration.md)

## Decision

Choose a bounded, import-only MATLAB-style text FIS profile for an
interoperability spike. Defer implementation in #425 until an independent
runtime evaluates the original fixture and a FuzzyRoutines consumer identifies
a model they would migrate. This decision authorizes fixture validation only.
The v1 JSON/YAML model remains the canonical representation.

## Evidence and implementation cost

- **IEC FCL.** The IEC catalog identifies IEC 61131-7:2000 as the fuzzy-control
  programming standard. The jFuzzyLogic reference example demonstrates a
  concrete FCL program consumed by a Java implementation, and FuzzyLite
  publishes FCL import/export examples. This establishes an interchange
  ecosystem, without identifying a FuzzyRoutines user with a PLC migration.
  Program blocks, piecewise term geometry, and default or retained output
  semantics increase cost. The v1 wire model does not carry general point
  functions, and the scalar engine raises on no firing. An FCL reader would
  need to reject those unsupported behaviors or wait for an explicit contract
  that represents them. [IEC catalog](https://webstore.iec.ch/en/publication/4556) ·
  [jFuzzyLogic FCL example](https://jfuzzylogic.sourceforge.net/html/example_fcl.html) ·
  [FuzzyLite](https://github.com/fuzzylite/fuzzylite/)
- **MATLAB FIS.** MathWorks documents text FIS read/write and distinguishes it
  from MAT files. GNU Octave's Fuzzy Logic Toolkit documents loading a text
  Sugeno model for evaluation, and FuzzyLite publishes MATLAB/Octave FIS
  examples. A MATLAB Central user also describes reusing an existing FIS
  in a FIS tree. These are public model exchange and reuse signals, without
  measuring demand from FuzzyRoutines users. The narrow text profile below
  can map to the current scalar model without a vendor runtime dependency.
  General FIS compatibility is costlier because it includes multiple outputs,
  type-2 models, more membership families, and alternative evaluation
  semantics. [MathWorks read](https://www.mathworks.com/help/fuzzy/readfis.html) ·
  [MathWorks write](https://www.mathworks.com/help/fuzzy/mamfis.writefis.html) ·
  [Octave toolkit](https://gnu-octave.github.io/packages/fuzzy-logic-toolkit/) ·
  [Octave model reuse example](https://octave.sourceforge.io/fuzzy-logic-toolkit/function/heart_disease_demo_2.html) ·
  [Consumer question](https://www.mathworks.com/matlabcentral/answers/2153480-how-to-import-an-already-made-fis-into-a-fis-tree-in-the-fuzzy-logic-designer)
- **IEEE FML.** IEEE 1855-2016 describes XML model interchange. JFML's
  published examples and the JFML IoT project demonstrate actual import
  integrations. The initial cost includes XML namespace and edition checks,
  secure parsing with external entities and DTDs disabled, and an explicit
  mapping for the selected system and rule base. The IoT use case does not
  establish demand for FuzzyRoutines. Revisit on a named FML consumer request.
  [IEEE 1855-2016](https://standards.ieee.org/ieee/1855/5418/) ·
  [JFML documentation](https://www.uco.es/JFML/documentation) ·
  [JFML IoT](https://github.com/JfMRes/JFML_IoT)

These sources support a bounded format preference. They do not establish
market share, broad conformance, or an obligation to implement any format.

## Proposed FIS import subset

Read one bounded text model. Require type-1 Sugeno, exactly one input and
one output, explicit finite closed ranges, strictly nondegenerate triangular
input terms, constant consequents, and weighted-average output. Require
positive in-range term and consequent indices and explicit product weights
in $[0,1]$. Use the explicit min/max operator pair for the one-input profile.
Resolve numbered declarations in source order and retain their display names.
Map the range to `ContinuousUniverse`, each `trimf` to `Triangle`, and each
rule to `SugenoRule` with a `TermCondition` and a
`ConstantConsequent`. Derive stable model-local IDs from declaration
positions. The decoded model must satisfy the same v1 shape and semantic
validation as other inputs. [Sugeno policies](https://www.mathworks.com/help/fuzzy/sugfis.html) ·
[Triangle formula](https://www.mathworks.com/help/fuzzy/trimf.html)

Reject unknown and duplicate sections or keys, unsupported operators,
affine and nonconstant outputs, omitted or negated indices, custom terms,
multiple outputs, Mamdani, type-2, FIS trees, and MAT. Read no dependent file
or executable expression. Reject malformed UTF-8, nonfinite numbers, numeric
overflow, unknown references, and limits exceeded with a location and
category. Use an explicit byte/record cap and reject on exhaustion. Never
execute FIS syntax, silently ignore an unsupported feature, or use a guessed
family alias.

Parity applies to in-domain successful evaluations of the documented subset.
Compare grades, firing strengths, declaration order and final values under
explicit tolerances. The scalar contract still raises on no fire and
out-of-range values. MATLAB can substitute an output-range midpoint when no
rule fires. That behavior is a known compatibility boundary, and no default
or prior output is synthesized. Names and rule ordering carry over. Source
layout, comments, vendor-specific metadata, and re-export are outside this
profile. A FIS input does not recreate historical preset identity or
representative-window semantics. [MATLAB evaluation options](https://www.mathworks.com/help/fuzzy/fuzzy.evalfis.evalfisoptions.html)

## Original numerical witness

Define input `load` on `[0, 4]` with `low` triangle `(0, 1, 3)` and
`high` triangle `(1, 3, 4)`. Define output `response` on `[0, 10]`.
Map `low` to constant 2 with weight 1 and `high` to constant 8 with
weight 0.5. At input 2 the grades are 0.5 and 0.5, the firing strengths
are 0.5 and 0.25, and the result is 4. At 0 both terms have grade zero,
which is a negative witness for the FuzzyRoutines no-fire contract.

The fixture values are original to this ADR. The acceptance spike still
needs a text FIS file emitted by a named tool and version, exact source
provenance, and an independent evaluation at these two inputs. Add rejection
fixtures for weighted sum, duplicate sections, and signed or zero rule
indices before proposing an installed reader.

## Licensing and next gate

Use primary documentation and originally authored fixtures. Repository and
standard licenses apply to their own materials. The JFML IoT repository
declares GPL-3.0, and no external implementation, schema, vendor sample
model, or standards text is included here. Reuse requires a separate
provenance and license decision. A future clean install must run without
MATLAB, Octave, a Java bridge, or network access.
