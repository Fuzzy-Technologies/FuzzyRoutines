# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Wire-level tests for the optional bounded YAML event reader."""

from importlib.util import find_spec as FindSpec
from math import copysign
from unittest import SkipTest

from fuzzyroutines._config_json import DecodeConfigJson, JsonConfigParseError, JsonNumber, JsonValue


def _DecodeYaml(encoded: bytes) -> JsonValue:
    """Use the optional backend when the test environment supplies it."""

    if FindSpec("yaml") is None:
        raise SkipTest("The YAML parser checkpoint requires PyYAML.")

    from fuzzyroutines._config_yaml import DecodeConfigYaml

    return DecodeConfigYaml(encoded)


def test_DecodesJsonSemanticsAndExactNumericTokens():
    """Keep JSON-compatible values, Unicode keys, and exact number spellings."""

    yaml = '"шкала": [-0, 9007199254740993, "🚀", true, null, "on", "${HOME}"]'.encode()
    json = '{"шкала":[-0,9007199254740993,"🚀",true,null,"on","${HOME}"]}'.encode()

    assert _DecodeYaml(yaml) == DecodeConfigJson(json), "YAML and JSON must produce equivalent wire trees."
    negativeZero = _DecodeYaml(b"-0")
    assert isinstance(negativeZero, JsonNumber) and copysign(1, negativeZero.binary64) == -1, (
        "YAML must preserve negative zero."
    )


def _Reject(encoded: bytes, pointer: str, message: str) -> None:
    """Require a stable wire diagnostic for one malformed YAML input."""

    try:
        _DecodeYaml(encoded)

    except JsonConfigParseError as failure:
        assert failure.pointer == pointer, f"Expected {pointer!r} for {encoded[:60]!r}, got {failure.pointer!r}."
        assert failure.category == "malformed-document", "YAML syntax failures must use the JSON wire category."
        assert message in str(failure), "YAML diagnostics must identify the failed guard."

    else:
        raise AssertionError(f"Unsafe YAML was accepted: {encoded[:60]!r}.")


def test_RejectsConstructionAndAmbiguousScalarsAtTheirPath():
    """Reject unsafe YAML features, duplicate keys, and non-JSON values."""

    cases = (
        (b'"a/b~c": [{same: 1, "same": 2}]', "/a~1b~0c/0/same", "Duplicate"),
        (b"entry: !!python/name:os.system ''", "/entry", "tags"),
        (b"entry: !include elsewhere.yml", "/entry", "tags"),
        (b"entry: &anchor [1]", "/entry", "anchors"),
        (b"entry: *anchor", "/entry", "aliases"),
        (b"entry: {<<: {sample: 1}}", "/entry/<<", "merge keys"),
        (b"entry: {1: a}", "/entry", "keys"),
        (b"entry: {[1, 2]: a}", "/entry", "keys"),
        (b"entry: .Inf", "/entry", "non-JSON"),
        (b"entry: 2026-11-06", "/entry", "non-JSON"),
        (b"entry: 012", "/entry", "non-JSON"),
        (b"entry: true\n---\nentry: false", "", "only one"),
        (b"%YAML 1.1\n---\nentry: false", "", "directives"),
        (b"entry: 1e309", "/entry", "overflows"),
        (b"entry: -1e-999", "/entry", "rounds to zero"),
        (b'entry: "\\uD800"', "/entry", "surrogate"),
        (b"entry: \xff", "", "UTF-8"),
        (b"\xef\xbb\xbf{}", "", "byte-order mark"),
    )

    for encoded, pointer, message in cases:
        _Reject(encoded, pointer, message)


def test_EnforcesExactStructuralBoundaries():
    """Reject input before a recursive or oversized tree can be created."""

    boundary = b" " * (1_048_576 - 2) + b"{}"
    assert _DecodeYaml(boundary) == {}, "Exactly 1,048,576 encoded bytes must be accepted."
    _Reject(boundary + b" ", "", "byte limit")
    depthBoundary = b"[" * 96 + b"]" * 96
    assert _DecodeYaml(depthBoundary) == DecodeConfigJson(depthBoundary), "Exactly 96 containers must be accepted."
    _Reject(b"[" + depthBoundary + b"]", "/0" * 96, "nesting limit")
    nodeBoundary = b"[" + b"null," * 65_534 + b"null"
    assert _DecodeYaml(nodeBoundary + b"]") == [None] * 65_535, "A list and its elements count against one budget."
    _Reject(nodeBoundary + b",null]", "/65535", "node limit")


def test_ReadsBlockCollectionsAndRejectsDeepAntecedents():
    """Handle readable block collections and keep the rule-depth boundary."""

    block = b"models:\n  sample:\n    values:\n      - 1.0\n      - false\n"
    assert _DecodeYaml(block) == DecodeConfigJson(b'{"models":{"sample":{"values":[1.0,false]}}}'), (
        "Block YAML must preserve the same shape and scalar types as JSON."
    )
    root = b"{inference: {rules: [{antecedent: "
    condition = b"{operand: " * 63 + b"{kind: term}" + b"}" * 63
    tail = b"}]}}"
    _DecodeYaml(root + condition + tail)
    _Reject(root + b"{operand: " + condition + b"}" + tail, "/inference/rules/0/antecedent" + "/operand" * 64, "64-node")


_PROJECT_JSON = (
    b'{"schemaVersion":1.0,"kind":"project","models":{"sample":'
    b'{"kind":"model","schemaVersion":1,"universes":{"unit":{"kind":"continuous",'
    b'"left":-0,"right":1,"leftClosed":true,"rightClosed":true}},'
    b'"memberships":{"mid":{"family":"triangle","parameters":{"left":0,"peak":5e-1,"right":1}}},'
    b'"scales":{"score":{"universe":"unit","terms":[{"id":"mid","membership":"mid",'
    b'"name":"on \\u0085 \\u2028 \\ufffe \\ud83d\\ude80"}]}}}},"defaults":{"model":"sample"}}'
)


def _RequireProjectExtras() -> None:
    """Keep semantic tests conditional on both explicit optional extras."""

    if any(FindSpec(name) is None for name in ("yaml", "jsonschema", "referencing")):
        raise SkipTest("YAML project validation requires the YAML and configuration extras.")


def test_ExportsStableYamlAndReusesProjectBindings():
    """Preserve the exact tree and reconstruct the same project via either format."""

    _RequireProjectExtras()

    from fuzzyroutines._config_project import DecodeProject
    from fuzzyroutines._config_yaml import ConvertProjectJsonToYaml, DecodeYamlProject

    yaml = ConvertProjectJsonToYaml(_PROJECT_JSON)
    assert yaml == ConvertProjectJsonToYaml(_PROJECT_JSON), "Exported YAML must be deterministic."
    assert yaml.startswith(b'"defaults":\n') and b'"peak": 5e-1\n' in yaml, (
        "Export must use sorted block mappings and preserve decimal spelling."
    )
    assert _DecodeYaml(yaml) == DecodeConfigJson(_PROJECT_JSON), (
        "YAML export must preserve strings, arrays and exact number tokens."
    )
    reference = DecodeProject(_PROJECT_JSON)
    project = DecodeYamlProject(yaml)
    assert project.defaults == reference.defaults and set(project.models) == set(reference.models), (
        "Both formats must bind the same project model and defaults."
    )


def test_ReportsSharedProjectValidationFailuresAtTheirPaths():
    """Apply the shared schema, version and semantic errors to YAML."""

    _RequireProjectExtras()

    from fuzzyroutines._config_json import ConfigurationError
    from fuzzyroutines._config_yaml import ConvertProjectJsonToYaml, DecodeYamlProject

    yaml = ConvertProjectJsonToYaml(_PROJECT_JSON)
    cases = (
        (yaml.replace(b'"schemaVersion": 1.0', b'"schemaVersion": 2'), "unsupported-version", "/schemaVersion"),
        (yaml + b'"include": "external"\n', "invalid-shape", "/include"),
        (yaml.replace(b'"model": "sample"', b'"model": "missing"'), "unresolved-reference", "/defaults/model"),
    )

    for encoded, category, pointer in cases:
        try:
            DecodeYamlProject(encoded)

        except ConfigurationError as error:
            assert (error.category, error.pointer) == (category, pointer), "YAML must preserve the v1 diagnostics."

        else:
            raise AssertionError(f"Expected {category!r} at {pointer!r}.")


def test_PublicByteConvertersValidateBothDirections():
    """Use one public bytes boundary without exposing project internals."""

    _RequireProjectExtras()

    from fuzzyroutines.configuration import ConfigurationError
    from fuzzyroutines.yaml_configuration import ConvertProjectJsonToYaml, ConvertProjectYamlToJson

    yaml = ConvertProjectJsonToYaml(_PROJECT_JSON)
    json = ConvertProjectYamlToJson(yaml)
    assert DecodeConfigJson(json) == DecodeConfigJson(_PROJECT_JSON), "Both converters must preserve the exact wire tree."
    assert b'"left":-0' in json and b'"peak":5e-1' in json, "Binary64 zero and exact decimal spellings must be retained."
    assert ConvertProjectJsonToYaml(json) == yaml, "The deterministic block output must survive a round trip."

    for converter, invalid in (
        (ConvertProjectJsonToYaml, b'{"kind":"project","schemaVersion":2,"models":{}}'),
        (ConvertProjectYamlToJson, b"kind: project\nschemaVersion: 2\nmodels: {}\n"),
    ):
        try:
            converter(invalid)

        except ConfigurationError as error:
            assert (error.category, error.pointer) == ("unsupported-version", "/schemaVersion"), (
                "Both public conversions must apply version validation before writing bytes."
            )

        else:
            raise AssertionError("The converters must reject an unsupported v1 version.")


def test_ProjectSnapshotRoundTripsAcrossFreshProcesses():
    """Save and restore a typed snapshot with the installed project API."""

    _RequireProjectExtras()

    from pathlib import Path
    from subprocess import run
    from sys import executable
    from tempfile import TemporaryDirectory

    import fuzzyroutines

    assert fuzzyroutines.__file__ is not None
    packageParent = str(Path(fuzzyroutines.__file__).resolve().parents[1])
    prelude = """
from pathlib import Path
import sys

sys.path.insert(0, sys.argv[1])
from fuzzyroutines.project_configuration import DumpProject, LoadProject
"""
    export = """
project = LoadProject(Path('source.json').read_bytes())
Path('project.json').write_bytes(DumpProject(project))
Path('project.yaml').write_bytes(DumpProject(project, formatName='yaml'))
"""
    restore = """
canonicalJson = Path('project.json').read_bytes()
canonicalYaml = Path('project.yaml').read_bytes()
project = LoadProject(canonicalYaml, formatName='yaml')
assert DumpProject(project) == canonicalJson
assert DumpProject(project, formatName='yaml') == canonicalYaml
assert b'\"left\":-0.0' in canonicalJson
assert project.SelectModel().scales['score'].termIds == ('mid',)
"""

    with TemporaryDirectory(prefix="fuzzyroutines-project-") as directory:
        projectRoot = Path(directory)
        (projectRoot / "source.json").write_bytes(_PROJECT_JSON)

        for program in (export, restore):
            result = run(
                [executable, "-I", "-c", prelude + program, packageParent],
                cwd=projectRoot,
                capture_output=True,
                check=False,
                text=True,
                timeout=15,
            )
            assert result.returncode == 0, result.stderr


def test_PublicYamlModuleImportsWithoutOptionalDependencies():
    """Keep YAML and schema dependencies lazy and report an absent backend."""

    from pathlib import Path
    from subprocess import run
    from sys import executable

    import fuzzyroutines

    assert fuzzyroutines.__file__ is not None
    packageParent = str(Path(fuzzyroutines.__file__).resolve().parents[1])
    result = run(
        [executable, "-S", "-c", """
import sys
from unittest.mock import patch

sys.path.insert(0, sys.argv[1])
from fuzzyroutines.yaml_configuration import ConvertProjectJsonToYaml

assert {"yaml", "jsonschema", "referencing"}.isdisjoint(sys.modules)
try:
    with patch("fuzzyroutines.yaml_configuration.FindSpec", return_value=None):
        ConvertProjectJsonToYaml(b"{}")
except ImportError as error:
    assert "fuzzyroutines[config,yaml]" in str(error)
else:
    raise AssertionError("A missing YAML backend must have actionable guidance.")
""", packageParent],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stderr
