<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Build a bounded linguistic scale

Use `fuzzyroutines.scale_builders.BuildLinearScale(terms, lower, upper)`
when adjacent labels should overlap. Supply ordered `(label, peak)` pairs and
a finite closed universe. Between adjacent peaks, two complementary linear
ramps share the grade. The first and last terms have flat shoulders out to
the respective endpoints. An endpoint peak is valid. For one term, its
grade is one throughout the universe.

Use `fuzzyroutines.scale_builders.BuildIntervalScale(labels, boundaries)`
when every coordinate should belong to exactly one bin. Supply one more
boundary than labels. An interior boundary belongs to the bin on its right,
and the final bin includes the upper endpoint.

Both functions return a `LinguisticScale` and preserve the order of labels.
Peaks and boundaries must be finite and strictly increasing. Labels must be
nonblank and unique under Unicode case folding. Coordinates outside the
closed universe raise the usual domain error during fuzzification.

For linear peaks at 0, 2, and 7, the ordered grades at 3 are
`(0, 4/5, 1/5)`. For bins with edges -2, 0, 2, and 9, the ordered grades at
3 are `(0, 0, 1)`. Within the universe, grades sum to one. Linear
interpolation uses exact ratios of integer, rational, and binary64 values.
Other real scalar types use their binary64 representation for interpolation.
