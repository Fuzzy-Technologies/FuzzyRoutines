<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Portable fuzzy configuration examples

[Русский](README.ru.md) · [简体中文](README.zh-CN.md)

[ADR-0021](../../adr/0021-versioned-project-configuration.md) proposes
the [version 1 schema](../../../fuzzyroutines/config-v1.schema.json). Install
`fuzzyroutines[config]` to load standalone model fixtures with
[`LoadModel`](../../site/content/en/api/modern/configuration.md) and write
canonical bytes with `DumpModel`. Both functions leave file access to the caller.
The project fixture illustrates inline models, presentation, and scenarios.
`LoadModel` accepts standalone model envelopes.

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
uses `jsonschema` 4.26.0 and `referencing`, available through the optional
`config` extra. The registry is offline.

```bash
python - <<'PY'
"""Verify the design fixtures against the bundled schema."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry

fixtureRoot = Path("docs/schemas/config-v1/fixtures")
schemaPath = Path("fuzzyroutines/config-v1.schema.json")
schema = json.loads(schemaPath.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, registry=Registry())

for path in sorted(fixtureRoot.glob("*.json")):
    document = json.loads(path.read_text(encoding="utf-8"))
    expected = not path.name.startswith("invalid-schema-")
    assert validator.is_valid(document) == expected, f"Unexpected schema outcome: {path}"
PY
```

The [callable case](fixtures/invalid-schema-callable.json) fails the schema
because its family and import parameters are outside the allowlist.
The [dangling-reference case](fixtures/invalid-semantic-reference.json)
passes the schema but must fail reference resolution. The expected error
from `LoadModel` points to `/scales/score/terms/0/membership` because the model
has no membership definition with ID `missing`. The two fixtures distinguish
schema validation from semantic reference resolution.

## YAML project verification

The optional `fuzzyroutines[yaml]` extra provides the YAML reader backend.
The installed project checks use `fuzzyroutines[config,yaml]` to exercise that
reader together with the offline v1 schema and project validator. YAML uses
the same project fields and scoped references as JSON. Tags, anchors, aliases,
merge keys and duplicate keys are rejected. A project field such as `include`
also fails the v1 schema. The tests check that conversion preserves numeric
tokens, Unicode and array order.

The public [YAML converters](../../site/content/en/api/modern/yaml.md) accept
and return validated project bytes. The reusable project snapshot API is
tracked separately in [#387](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/387).
