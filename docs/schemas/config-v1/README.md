<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Portable fuzzy configuration examples

[Русский](README.ru.md) · [简体中文](README.zh-CN.md)

[ADR-0021](../../adr/0021-versioned-project-configuration.md) proposes
the [version 1 schema](../config-v1.schema.json). These JSON files are design
fixtures. They can be checked with a JSON Schema validator; FuzzyRoutines does
not load them in this change.

- [Historical scale](fixtures/valid-historical-scale.json) stores the five
  original terms, their coefficients, the closed unit universe, the
  per-term centroid windows, and last-exact-maximum selection. For example,
  the input `0.75` selects `High` with membership `1`.
- [Discrete scale](fixtures/valid-discrete-scale.json) evaluates an analytical
  Harrington function only at the three declared coordinates. It does not
  interpolate between coordinates in the discrete universe.
- [Project](fixtures/valid-project.json) contains a Mamdani model called
  `centroid` and a Sugeno model called `weighted`. The `quarter` scenario
  selects `weighted` at `risk = 0.25`. Its rules fire at `0.875` and `0.125`
  with consequents `0.25` and `0.625`; the weighted result is `0.296875`.
  At the same input the Mamdani model clips a symmetric triangle, with
  centroid `0.5`. The project title, color, and displayed unit do not enter
  either calculation.

Edit model definitions to change the mathematics. To change a graph label
or color, edit `presentation`. A reference must use the ID of a definition
in the correct scope; for instance, the scenario binds `risk`, the input ID,
even though the runtime variable is named `Risk`.

## Checking the files

Run from the repository root with a Draft 2020-12 validator. This example
uses `jsonschema` 4.26.0 in a separate validation environment; it is not a
package dependency. The registry is offline.

```bash
python - <<'PY'
"""Verify the design fixtures against the bundled schema."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry

schema_root = Path("docs/schemas")
schema = json.loads((schema_root / "config-v1.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, registry=Registry())

for path in sorted((schema_root / "config-v1" / "fixtures").glob("*.json")):
    document = json.loads(path.read_text(encoding="utf-8"))
    expected = not path.name.startswith("invalid-schema-")
    assert validator.is_valid(document) == expected, f"Unexpected schema outcome: {path}"
PY
```

The [callable case](fixtures/invalid-schema-callable.json) fails the schema
because its family and import parameters are outside the allowlist.
The [dangling-reference case](fixtures/invalid-semantic-reference.json)
passes the schema but must fail reference resolution. The expected error
points to `/scales/score/terms/0/membership`: there is no membership definition
with ID `missing` in that model. The design fixtures distinguish structural
validation from the semantic checks a future loader must perform.
