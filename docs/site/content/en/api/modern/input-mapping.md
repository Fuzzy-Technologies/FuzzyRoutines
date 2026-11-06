<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Affine input mapping

Use `AffineInputMapping` to turn a physical observation into a coordinate
in an existing finite, closed continuous universe. Declare both units and
the physical bounds when constructing the mapping. Use `1` for a
dimensionless coordinate. The mapping checks unit labels exactly and
rejects observations outside the declared interval. A missing observation
raises `MissingObservationError`.

The example maps 30 °C from an operating range of 10–50 °C to 0.5 on the
unit interval. The inverse returns 30 °C in this case. Endpoint anchors are
exact. Interior coordinates round to binary64 and can limit the accuracy
of an inverse round trip. A v1 project scenario still takes scale
coordinates. Apply the mapping before constructing the scenario.

```python
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.input_mapping import AffineInputMapping, MissingObservationError

universe = ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True)
mapping = AffineInputMapping(10, 50, universe, "°C", "1")
coordinate = mapping.Forward(30, unit="°C")
assert coordinate == 0.5
assert universe.Contains(coordinate)
assert mapping.Inverse(coordinate, unit="1") == 30

try:
    mapping.Forward(None, unit="°C")
except MissingObservationError as error:
    missing = error
else:
    raise AssertionError("Expected a missing-observation error.")
```

::: fuzzyroutines.input_mapping
