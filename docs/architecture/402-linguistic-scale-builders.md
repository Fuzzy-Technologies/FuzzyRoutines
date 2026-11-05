<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Linguistic scale builder contract

Status: draft design for [#402](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/402).

Provide two constructors returning the existing immutable `LinguisticScale`
over a single finite, closed `ContinuousUniverse`. All terms share the
universe, so normal scale fuzzification applies at every declared coordinate.

- A linear scale takes ordered (label, peak) pairs and explicit lower and
  upper bounds. Between adjacent peaks, exactly two neighboring terms
  share membership by complementary linear ramps. Each peak owns itself
  at grade one. The first and last terms extend as flat shoulders from
  their peaks to the corresponding domain endpoints. One term is grade
  one throughout the domain.
- An interval scale takes ordered labels and one more strictly increasing
  boundary than labels. Each bin includes its left boundary and excludes
  its right boundary, except the final bin which includes the global
  upper bound. Exactly one term owns every coordinate.

Empty labels, case-fold duplicate labels, non-finite coordinates, repeated
or crossed peaks or boundaries, peaks outside the closed domain and
incorrect tuple shapes fail at construction. A shoulder peak may coincide
with the corresponding universe endpoint because its plateau then has
zero width. Out-of-domain evaluation keeps the existing scalar error.

The interval grades sum to one exactly. Linear grades sum to one in exact
arithmetic, and the implementation will test an absolute binary64 tolerance
for the rounded grades. Coverage and partition claims apply inside the
declared universe and do not modify the historical Universal Fuzzy Scale.
No sampled point is used as a substitute for these constructions.

Independent hand witnesses use peaks 0, 2 and 7 on the domain [-2, 9].
The ordered linear grades at -2, 1, 3, 7 and 9 are (1, 0, 0), (1/2, 1/2, 0),
(0, 4/5, 1/5), (0, 0, 1) and (0, 0, 1). For three interval bins with boundaries
-2, 0, 2 and 9, the owner of -2 is the first term, 0 the second term, and
2 and 9 the third term. Tests will compare the builders against a scale
assembled directly from independently authored scalar callbacks.
