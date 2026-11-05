<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Interval Type-2 reduction for a synthetic latency threshold

**Status:** Research draft for [Task #429][task]. Keep this experiment outside the installed API.

## Context

A service operator has two increasing CPU-load thresholds that describe where
nominal response starts to lose support and where overload starts to gain
support. Each threshold can vary independently by five percentage points
between expert configurations. At fixed CPU load, the extremal thresholds
bound the possible membership grades. Crisp constants of 100 ms and 260 ms
provide the two zero-order Sugeno consequents. All values are illustrative.

## Decision

At a fixed input, allow any combination of firing strengths within the two
closed intervals. This is a box assumption about the rule weights. A shared
uncertain threshold or other coupling would constrain feasible combinations
and could shrink the range. At each extreme weighted average, coefficients
of consequences on one side of the average can take one endpoint and
coefficients on the other side can take the opposite endpoint. Sort the
consequences and scan every switch point in both orientations. Ignore the
all-zero candidate when positive firing is feasible and fail explicitly if
every rule has zero upper firing. This bounded reference scans at most 33
switch points per orientation and uses exact rational accumulation for
each selected set of binary64 values.

The output is a range of model responses under the declared membership
uncertainty. Statistical prediction coverage would require separate data
and calibration. See [Mendel, John and Liu][mendel] for interval Type-2
systems and [Haghrah et al.][pyit2fls] for an external toolbox candidate.

## Evidence and next decision

Run from the repository root.

```console
python -m research.interval_type2.monitoring
python -m pytest -q tests/test_research_interval_type2.py
```

At 80% CPU load, the zero-width scalar case gives about 191.429 ms.
The interval result spans 168.571–214.286 ms, crossing a 200 ms alert
threshold. The deterministic checks compare both extrema against exhaustive
box vertices, including zero lower firing and repeated consequences. They
also compare the collapsed interval with the existing scalar Sugeno engine,
exercise the empty-firing failure, and cover membership ordering on the
synthetic input grid.

The prototype supports a documentation example after independent scientific
review. The public API remains deferred pending evidence from a service
dataset, agreement with a version-pinned external implementation, and a
separate scope decision about coupled firing strengths.

[task]: https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/429
[mendel]: https://doi.org/10.1109/TFUZZ.2006.879986
[pyit2fls]: https://doi.org/10.1016/j.softx.2025.102146
