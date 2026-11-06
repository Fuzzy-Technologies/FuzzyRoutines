<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# YAML project configuration

Install `fuzzyroutines[config,yaml]` to convert project documents.
`[yaml]` provides the parser and `[config]` provides the offline v1 schema
validator. Both converters accept and return bounded UTF-8 bytes. The caller
opens and writes files explicitly. Conversion checks the schema and resolves
project references without running inference or evaluating scenarios.

YAML accepts a single data document with string keys. Duplicate keys, explicit
tags, anchors, aliases and merge keys raise
[`ConfigurationError`](configuration.md).
An unknown version or a field such as `include` fails validation. The error
provides a category and JSON Pointer. Conversion preserves number tokens and
array order, sorts mappings, and leaves the original document untouched.

The example converts a project containing a triangular scale in both directions.
The signed zero and exponential number spelling survive the round trip.

```python
from fuzzyroutines.yaml_configuration import ConvertProjectJsonToYaml, ConvertProjectYamlToJson

projectJson = b'''{
  "kind": "project", "schemaVersion": 1,
  "models": {"score": {
    "kind": "model", "schemaVersion": 1,
    "universes": {"unit": {"kind": "continuous", "left": -0, "right": 1, "leftClosed": true, "rightClosed": true}},
    "memberships": {"middle": {"family": "triangle", "parameters": {"left": 0, "peak": 5e-1, "right": 1}}},
    "scales": {"score": {"universe": "unit", "terms": [{"id": "middle", "name": "Middle", "membership": "middle"}]}}
  }}
}'''
projectYaml = ConvertProjectJsonToYaml(projectJson)
canonicalJson = ConvertProjectYamlToJson(projectYaml)

assert b'"left":-0' in canonicalJson
assert b'"peak":5e-1' in canonicalJson
assert ConvertProjectJsonToYaml(canonicalJson) == projectYaml
```

::: fuzzyroutines.yaml_configuration
    options:
      members:
        - ConvertProjectJsonToYaml
        - ConvertProjectYamlToJson
