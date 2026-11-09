<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Portable project configuration

Use `LoadProject` and `DumpProject` to restore and save a validated v1 project
snapshot. It contains named inline models, optional defaults, display units,
plot settings and evaluation scenarios. Use
[`LoadModel` and `DumpModel`](configuration.md) for a standalone model.

## Convert documents without building a snapshot

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

## Restore and save a typed project snapshot

Install `fuzzyroutines[config]` for JSON or `fuzzyroutines[config,yaml]` to
include YAML. Pass `formatName="yaml"` for YAML bytes. The default is JSON.
Project loading and export use the same bundled v1 schema. The snapshot
keeps the model mathematics and the presentation settings separate. Loading
checks references throughout the project without running inference or
drawing a plot. Both functions work with bytes. The caller chooses the
file paths and performs all reads and writes. V1 project documents contain
no includes, external references or output paths.

Model IDs are case-sensitive. `SelectModel("score")` selects that exact
model. `SelectModel()` uses the declared model default and raises `KeyError`
when it is absent, even if the project has only one model.

The example checks deterministic export within each format. After restoring
from YAML, it inspects the ordered scale terms, display units, plot color
and saved inputs before evaluating the model explicitly. The single Sugeno
rule fires at the saved input and returns `0.75`.

```python
from fuzzyroutines.configuration import SugenoBinding
from fuzzyroutines.project_configuration import DumpProject, LoadProject

projectJson = b'''{
  "kind": "project", "schemaVersion": 1,
  "models": {"score": {
    "kind": "model", "schemaVersion": 1,
    "universes": {"unit": {
      "kind": "continuous", "left": 0, "right": 1,
      "leftClosed": true, "rightClosed": true
    }},
    "memberships": {
      "middle": {"family": "triangle", "parameters": {"left": 0, "peak": 0.5, "right": 1}},
      "high": {"family": "s_shoulder", "parameters": {"left": 0, "right": 1}}
    },
    "scales": {"risk": {"universe": "unit", "terms": [
      {"id": "middle", "name": "Middle", "membership": "middle"},
      {"id": "high", "name": "High", "membership": "high"}
    ]}},
    "inference": {
      "kind": "sugeno", "outputUniverse": "unit",
      "inputs": [{"id": "risk", "name": "Risk", "scale": "risk"}],
      "policy": {"conjunction": "logic", "disjunction": "logic", "negation": {"family": "standard"}},
      "rules": [{
        "id": "respond", "name": "Respond", "weight": 1,
        "antecedent": {"kind": "term", "input": "risk", "term": "high"},
        "consequent": {"kind": "constant", "value": 0.75}
      }]
    }
  }},
  "defaults": {"model": "score", "plot": "curve", "evaluation": "quarter"},
  "presentation": {
    "units": {"score": {"unit": "ratio"}},
    "plots": {"curve": {"model": "score", "scale": "risk", "termColors": {"high": "#8E44AD"}}}
  },
  "evaluations": {"quarter": {"model": "score", "inputs": {"risk": 0.25}, "trace": true}}
}'''
snapshot = LoadProject(projectJson)
yamlBytes = DumpProject(snapshot, formatName="yaml")
restored = LoadProject(yamlBytes, formatName="yaml")

assert DumpProject(restored, formatName="yaml") == yamlBytes
assert DumpProject(restored) == DumpProject(snapshot)

defaults = restored.defaults
assert defaults is not None
assert (defaults.modelId, defaults.plotId, defaults.evaluationId) == ("score", "curve", "quarter")
model = restored.SelectModel()
assert model.scales["risk"].termIds == ("middle", "high")
assert restored.units["score"]["unit"] == "ratio"
assert restored.plots["curve"].termColors["high"] == "#8E44AD"

scenario = restored.evaluations["quarter"]
assert scenario.trace
binding = model.inference
assert isinstance(binding, SugenoBinding)
result = binding.model.Evaluate({"Risk": scenario.inputs["risk"]})
assert result.value == 0.75
```

::: fuzzyroutines.project_configuration
    options:
      members:
        - LoadProject
        - DumpProject
        - ProjectSnapshot
        - ProjectDefaults
        - ProjectPlot
        - ProjectEvaluation
