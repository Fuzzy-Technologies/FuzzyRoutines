# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Static type-alias documentation and translation drift regression contracts."""

from tools.documentation_gates import ValidateCoverage
from tools.locale_documentation import CanonicalHash, DiscoverCanonicalUnits

ALIAS_SOURCE = '''raise RuntimeError("Documentation discovery must never import source")

type Scalar = float | int
"""Accept built-in numeric scalar annotations."""

type _Internal = str
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
