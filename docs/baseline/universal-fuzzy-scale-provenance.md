<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Historical UniversalFuzzyScale preset

## Status and boundary

This document freezes the legacy preset exactly as it exists on the v2 baseline. It is a provenance record, not a claim that the coefficients are mathematically universal or suitable for new models. No coefficient tuning is included in Task #86.

## Preset identity

| Order | Level | Membership family | Parameters             | Support      | Linguistic name |
|-------|-------|-------------------|------------------------|--------------|-----------------|
| 1     | Min   | hyperbolic        | a=8, b=20, c=0         | [0.00, 0.23] | Min             |
| 2     | Low   | bell              | a=0.17, b=0.23, c=0.34 | [0.17, 0.40] | Low             |
| 3     | Med   | bell              | a=0.34, b=0.40, c=0.60 | [0.34, 0.66] | Med             |
| 4     | High  | bell              | a=0.60, b=0.66, c=0.77 | [0.60, 0.83] | High            |
| 5     | Max   | parabolic         | a=0.77, b=0.95         | [0.77, 1.00] | Max             |

The historical scale name is FuzzyScale. Its level-name lookup maps preserve the case-sensitive and uppercase forms exposed by the legacy API.

## Executable evidence

- Task #87 freezes construction, order, identifiers, coefficients, supports, centroids, and representative selections.
- Task #88 provides a deterministic coverage diagnostic and reports weak regions without changing this preset.
- Task #78 records the historical centroid routine used during construction.

Any future renamed or retuned scale must be introduced as a separately named preset with its own contract and migration note.
