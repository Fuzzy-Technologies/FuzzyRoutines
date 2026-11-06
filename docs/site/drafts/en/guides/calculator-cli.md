<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Standalone JSON calculator {#standalone-json-calculator}

Use the installed `fuzzyroutines` command to validate a standalone v1 JSON
model, evaluate one membership grade, classify a coordinate, or run scalar
Mamdani or Sugeno inference. This 2.2 checkpoint covers standalone `.json`
models. Project envelopes, YAML and plot commands are tracked separately.

## Install the command {#install}

In a fresh CPython 3.13 or 3.14 environment, point `FUZZYROUTINES_WHEEL`
to the absolute path of the reviewed wheel containing this CLI. Install its
`config` extra for schema validation. Help and version write plain text to
stdout and also work with the base wheel. Version prints the wheel's metadata
version.

```bash
: "${FUZZYROUTINES_WHEEL:?Set the absolute path to the reviewed CLI wheel}"
python -m pip install "${FUZZYROUTINES_WHEEL}[config]"
fuzzyroutines --help
fuzzyroutines --version
```

## Create a model {#model}

Save this Sugeno model from a POSIX shell. Keep the quotes around the Unicode
file name, which contains a space. Each command resolves relative paths from
the working directory.

```bash
cat > 'модель α.json' <<'JSON'
{
  "kind": "model",
  "schemaVersion": 1,
  "universes": {"unit": {"kind": "continuous", "left": 0, "right": 1, "leftClosed": true, "rightClosed": true}},
  "memberships": {"triangle": {"family": "triangle", "parameters": {"left": 0, "peak": 0.5, "right": 1}}},
  "scales": {
    "risk": {
      "universe": "unit",
      "terms": [{"id": "middle", "name": "Middle", "membership": "triangle"}],
      "representatives": {
        "windows": {"middle": {"left": 0, "right": 1}},
        "policy": {"absoluteTolerance": 1e-12, "relativeTolerance": 1e-10, "maximumDepth": 20}
      }
    }
  },
  "inference": {
    "kind": "sugeno",
    "inputs": [{"id": "risk", "name": "Risk", "scale": "risk"}],
    "policy": {"conjunction": "logic", "disjunction": "logic", "negation": {"family": "standard"}},
    "rules": [{
      "id": "balanced",
      "name": "Balanced",
      "antecedent": {"kind": "term", "input": "risk", "term": "middle"},
      "consequent": {"kind": "constant", "value": 0.25},
      "weight": 1
    }],
    "outputUniverse": "unit"
  }
}
JSON
```

The triangle peaks at 0.5 and has grade 0.5 at 0.25. The single rule returns
0.25 whenever it fires. Membership grades are degrees of membership.

## Evaluate from the shell {#evaluate}

`--project` supplies the file even when it holds a standalone model. Use the
case-sensitive IDs `risk` and `middle`. `Middle` is its display label.
A standalone model has no `--model` or `--evaluation` selector.

```bash
fuzzyroutines validate --project 'модель α.json'
fuzzyroutines membership --project 'модель α.json' --scale risk --term middle --x 0.25
fuzzyroutines fuzzify --project 'модель α.json' --scale risk --x 0.25
fuzzyroutines infer --project 'модель α.json' --input 'risk=0.5'
```

Each line below is a separate result on stdout, in command order. Machine
results use sorted keys and one trailing LF. Arrays retain model order.

```json
{"command":"validate","result":{"kind":"model","schemaVersion":1},"resultVersion":1}
{"command":"membership","result":{"coordinate":0.25,"grade":0.5,"scale":"risk","term":"middle"},"resultVersion":1}
{"command":"fuzzify","result":{"confidence":0.5,"coordinate":0.25,"match":true,"memberships":[{"grade":0.5,"term":"middle"}],"scale":"risk","selectedTerms":["middle"],"tiedTerms":["middle"]},"resultVersion":1}
{"command":"infer","result":{"kind":"sugeno","method":"normalized-weighted-average","value":0.25},"resultVersion":1}
```

## Encode a term explicitly {#representatives}

`--term-input` selects a term ID on the input's scale and requires
`--encoding representative-centroid`. For this symmetric triangle, the
declared window `[0, 1]` gives the representative 0.5. The encoded
coordinate undergoes the same domain validation as a numeric input.
Supply each input once, either numerically or by term. Add `--explain`
to inspect the ordered membership and rule evidence.

```bash
fuzzyroutines infer --project 'модель α.json' --term-input 'risk=middle' --encoding representative-centroid --explain
```

```json
{"command":"infer","result":{"kind":"sugeno","method":"normalized-weighted-average","trace":{"inputGrades":[{"grade":1.0,"input":"risk","term":"middle"}],"rules":[{"antecedentGrade":1.0,"consequentValue":0.25,"contribution":0.25,"firingStrength":1.0,"normalizedStrength":1.0,"rule":"balanced","weight":1.0}]},"value":0.25},"resultVersion":1}
```

## Handle failures in scripts {#errors}

Exit `0` indicates success. A failed invocation leaves stdout empty and
writes one JSON object to stderr. Handle the exit status and `error.category`.
Diagnostic wording can change.

- `2` (`usage`) covers invalid options, numbers or bindings.
- `3` (`configuration`) covers invalid or unsupported configuration. Codec
  errors include `detailCategory` and an RFC 6901 `pointer`.
- `4` (`evaluation`) covers a domain violation, undefined representative,
  or inference with no firing rule.
- `5` (`io`) covers a file access failure.
- `6` (`capability`) covers missing optional support.

At coordinate 0 the only term has grade zero, so this model exits `4`.

```bash
fuzzyroutines infer --project 'модель α.json' --input 'risk=0'
```

```json
{"error":{"category":"evaluation","message":"inference is undefined because no rule fires"},"resultVersion":1}
```

With a base wheel installed without `[config]`, `validate` on the valid
model exits `6` and writes this diagnostic.

```json
{"error":{"category":"capability","message":"Install fuzzyroutines[config] to validate model configuration."},"resultVersion":1}
```

With `[config]` installed, a duplicated `kind` key produces exit `3`.
The pointer identifies the duplicate field.

```bash
printf '{"kind":"model","kind":"model"}\n' > 'ошибка α.json'
fuzzyroutines validate --project 'ошибка α.json'
```

```json
{"error":{"category":"configuration","detailCategory":"malformed-document","message":"Duplicate JSON object key.","pointer":"/kind"},"resultVersion":1}
```

See the [JSON configuration API](../../../content/en/api/modern/configuration.md) for the
Python equivalents of model loading and saving.
