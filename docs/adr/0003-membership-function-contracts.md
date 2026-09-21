<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0003: Membership-Function Parameter Conventions and Validation

- Status: Accepted on merge
- Date: 2026-09-14
- Related planning task: #10
- Related Feature: #18

## Context

The legacy `MFunction` factory uses concise historical identifiers and parameter
names. In particular, `Triangle` and `Trapezium` use an ordering different
from the common left-to-right convention. A modernization that silently adopts
a textbook ordering would produce valid-looking but incorrect results for
existing callers.

## Decision

Historical identifiers, keyword names, and meanings remain protected by
ADR-0001. The following table records the legacy contract implemented by
`fuzzyroutines.FuzzyRoutines.MFunction`.

| Identifier       | Historical parameters   | Meaning                                                                                                                                          |
|------------------|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| `hyperbolic`     | `a, b, c`               | `c` is the left shoulder cutoff; for `x > c`, `a` is the scale and `b` the exponent in `1 / (1 + (a(x-c))^b)`.                                   |
| `bell`           | `a, b, c`               | `a` is the left foot, `b` the plateau start, `c` the plateau end; the right foot is derived as `c + b - a`.                                      |
| `parabolic`      | `a, b`                  | `a` is the left foot and `b` the right plateau boundary.                                                                                         |
| `triangle`       | `a, b, c`               | `a` is the left foot, **`c` is the apex**, and `b` is the right foot. Validation requires `a < c <= b`; `c = b` preserves the default high term. |
| `trapezium`      | `a, b, c, d`            | `a` is the left foot, `c` the plateau start, `d` the plateau end, and `b` the right foot. Validation requires `a < c <= d < b`.                  |
| `exponential`    | `a, b`                  | `a` is the centre and `b` is the non-zero scale in the Gaussian-shaped expression.                                                               |
| `sigmoidal`      | `a, b`                  | `a` is the slope and `b` is the midpoint.                                                                                                        |
| `desirability`   | none                    | Harrington desirability uses the input `y` and no stored parameters.                                                                             |

The implementation Tasks must explicitly decide whether strict inequalities are
needed for non-degenerate shapes. Degenerate parameter combinations must never
be silently converted into plausible membership values.

## Validation policy

Future validation accepts only finite real inputs and parameters that satisfy
the family contract. Invalid configurations must raise a clear domain error;
they must not be swallowed and converted to a membership value of zero.

The decision does not change the historical parameter ordering. Modern
left-to-right aliases may be added only under different, explicit names and
only after the legacy behavior is covered by regression tests.

## Implementation matrix

- Task #50 owns publication of the user-facing reference table.
- Task #51 owns strict validation implementation.
- Task #52 owns reference and property tests.
- Task #53 removes Bell's evaluation-time parameter mutation.
- Task #54 adds exact compatibility registry names that dispatch to the same
  interim implementation: `sShoulder`, `gaussian`, `logistic`, and
  `harringtonDesirability`.

The contract is enforced by Task #51 and covered by the reference/property
suite from Task #52.

## Consequences

A common `(left, peak, right)` or
`(left, plateau_start, plateau_end, right)` API must not be passed through to
the legacy `triangle` or `trapezium` identifiers. It requires a separate
modern alias with an unambiguous name.

The current `MFunction` aliases do not duplicate formulas. They are additional
keys in the legacy factory registry and therefore share one bound method and
validated parameter contract. This is a transitional compatibility mechanism,
not the final direction of ownership: focused modern modules will own the
canonical implementations, while historical identifiers delegate to or adapt
those implementations through `FuzzyRoutines.py`.

A conventional registry alias is deliberately absent for the non-standard
flat-top `bell`, legacy-order `triangle`, and legacy-order `trapezium`
families. Their modern replacements require explicit conventional parameter
contracts rather than ambiguous pass-through aliases.

## Acceptance and supersession

This ADR is **Accepted**. A future family added to `MFunction`, or a change to
a recorded convention, requires an amendment or a new ADR and compatibility
evidence.
