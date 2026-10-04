# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Static type-alias documentation and translation drift regression contracts."""

import pytest

from tools.documentation_gates import ValidateCoverage
from tools.locale_documentation import CanonicalHash, DiscoverCanonicalUnits

ALIAS_SOURCE = '''raise RuntimeError("Documentation discovery must never import source")

type Scalar = float | int
"""Accept built-in numeric scalar annotations."""

type _Internal = str
'''

OVERLOAD_SOURCE = '''raise RuntimeError("Documentation discovery must never import source")
from typing import overload

@overload
def Scalar(value: int) -> int:
    """Describe the integer signature."""
    ...

@overload
def Scalar(value: str) -> str:
    """Describe the string signature."""
    ...

def Scalar(value: int | str) -> int | str:
    """Preserve the complete concrete implementation contract."""
    return value
'''


def _Prepare(project_root, source=ALIAS_SOURCE, selected="Scalar"):
    """Write an intentionally unimportable source and explicit alias export."""

    paths = {
        "fuzzyroutines/__init__.py": 'from fuzzyroutines.membership import Scalar\n__all__ = ["Scalar"]\n',
        "fuzzyroutines/membership.py": source,
        "docs/site/content/en/api.md": f"# API\n\n::: fuzzyroutines.membership\n    options:\n      members:\n        - {selected}\n",
        "docs/site/api-coverage.toml": '''schemaVersion = 1

[[surfaces]]
module = "fuzzyroutines"
source = "fuzzyroutines/__init__.py"
mode = "exports"

[[surfaces]]
module = "fuzzyroutines.membership"
source = "fuzzyroutines/membership.py"
mode = "authored"
''',
    }

    for relative_path, content in paths.items():
        path = project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return {
        "contentRoot": "docs/site/content",
        "apiCoverageManifest": "docs/site/api-coverage.toml",
        "packageNames": ["fuzzyroutines"],
    }


def test_TypeAliasesRetainCanonicalDocstringsAndExportIdentities(tmp_path):
    """Discover PEP 695 aliases without imports or private-name leakage."""

    manifest = _Prepare(tmp_path)
    units = {unit.identifier: unit for unit in DiscoverCanonicalUnits(tmp_path, manifest) if unit.kind == "symbol"}

    assert set(units) == {"symbol:fuzzyroutines.Scalar", "symbol:fuzzyroutines.membership.Scalar"}, (
        "Static discovery must include authored and exported aliases without private definitions"
    )

    for unit in units.values():
        assert unit.signature == "type Scalar = float | int", "Alias hashing must include its full definition"
        assert unit.body == "Accept built-in numeric scalar annotations.", (
            "Alias documentation must come from the immediately following source string"
        )
        assert unit.sourcePath == "fuzzyroutines/membership.py", "Exports must retain canonical source ownership"

    assert ValidateCoverage(projectRoot=tmp_path) == (), "A rendered and documented public alias must pass coverage"


def test_TypeAliasDefinitionAndDocumentationChangesInvalidateHashes(tmp_path):
    """Include alias signatures and source contracts in translation freshness."""

    manifest = _Prepare(tmp_path)
    before = {unit.identifier: CanonicalHash(unit) for unit in DiscoverCanonicalUnits(tmp_path, manifest) if unit.kind == "symbol"}

    for source in (
        ALIAS_SOURCE.replace("float | int", "float | complex"),
        ALIAS_SOURCE.replace("numeric scalar", "finite scalar"),
    ):
        _Prepare(tmp_path, source=source)
        after = {unit.identifier: CanonicalHash(unit) for unit in DiscoverCanonicalUnits(tmp_path, manifest) if unit.kind == "symbol"}
        assert all(after[identifier] != digest for identifier, digest in before.items()), (
            "Changing alias signatures or documentation must invalidate both canonical hashes"
        )


def test_UndocumentedOrUnrenderedTypeAliasesFailCoverage(tmp_path):
    """Keep alias export support from bypassing documentation coverage."""

    _Prepare(tmp_path, source=ALIAS_SOURCE.replace('"""Accept built-in numeric scalar annotations."""\n', ""))
    errors = ValidateCoverage(projectRoot=tmp_path)
    assert any("fuzzyroutines.membership.Scalar has no source docstring" in error for error in errors), (
        "Public aliases without source documentation must fail coverage"
    )

    _Prepare(tmp_path, selected="Missing")
    errors = ValidateCoverage(projectRoot=tmp_path)
    assert any("fuzzyroutines.membership.Scalar is public but absent" in error for error in errors), (
        "Public aliases omitted from reference selections must fail coverage"
    )


def test_OverloadsRetainOneIdentityAndConcreteDocumentation(tmp_path):
    """Select concrete contracts while preserving every overload signature."""

    manifest = _Prepare(tmp_path, source=OVERLOAD_SOURCE)
    units = [unit for unit in DiscoverCanonicalUnits(tmp_path, manifest) if unit.kind == "symbol"]
    assert len(units) == 2, "Overload stubs must not duplicate authored or exported identities"
    assert {unit.identifier for unit in units} == {
        "symbol:fuzzyroutines.Scalar", "symbol:fuzzyroutines.membership.Scalar",
    }, "Both public identities must resolve statically to the concrete implementation"

    for unit in units:
        assert unit.body == "Preserve the complete concrete implementation contract.", (
            "Overload summaries must not replace the full implementation documentation"
        )
        assert unit.signature.splitlines() == [
            "def Scalar(value: int) -> int",
            "def Scalar(value: str) -> str",
            "def Scalar(value: int | str) -> int | str",
        ], "Canonical hashes must retain ordered overload and implementation signatures"

    assert ValidateCoverage(projectRoot=tmp_path) == (), "Documented overload implementations must pass coverage"


def test_OverloadOnlyChangesInvalidateCanonicalHashes(tmp_path):
    """Detect a changed overload even when the implementation stays identical."""

    manifest = _Prepare(tmp_path, source=OVERLOAD_SOURCE)
    before = {unit.identifier: CanonicalHash(unit) for unit in DiscoverCanonicalUnits(tmp_path, manifest) if unit.kind == "symbol"}
    _Prepare(tmp_path, source=OVERLOAD_SOURCE.replace("value: str) -> str", "value: bytes) -> bytes"))
    after = {unit.identifier: CanonicalHash(unit) for unit in DiscoverCanonicalUnits(tmp_path, manifest) if unit.kind == "symbol"}
    assert all(after[identifier] != digest for identifier, digest in before.items()), (
        "Overload-only edits must invalidate both exported and authored translation hashes"
    )


def test_OverloadStubsCannotSubstituteForConcreteContracts(tmp_path):
    """Reject missing concrete implementations and missing implementation docs."""

    manifest = _Prepare(tmp_path, source=OVERLOAD_SOURCE.split("\ndef Scalar(value: int | str)")[0])

    with pytest.raises(ValueError, match="cannot find public definition Scalar"):
        DiscoverCanonicalUnits(tmp_path, manifest)

    _Prepare(tmp_path, source=OVERLOAD_SOURCE.replace('    """Preserve the complete concrete implementation contract."""\n', ""))
    errors = ValidateCoverage(projectRoot=tmp_path)
    assert any("fuzzyroutines.membership.Scalar has no source docstring" in error for error in errors), (
        "Stub docstrings must not hide an undocumented implementation"
    )
