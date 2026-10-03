# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Preserve public documentation identities after explicit adapter extraction."""

import pytest

from tools.documentation_gates import ValidateCoverage
from tools.locale_documentation import CanonicalHash, DiscoverCanonicalUnits

AUTHORED_SOURCE = '''raise RuntimeError("Static discovery must never import this source")

class Visible:
    """Expose a stable public class contract."""

    def Evaluate(self, value):
        """Return the supplied grade."""

        return value

def Function(value):
    """Return a stable public function result."""

    return value
'''


def _Write(path, content):
    """Write one static fixture while retaining a normal project layout."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _Prepare(project_root, mode="adapters", imports=None, source=AUTHORED_SOURCE):
    """Prepare a facade and an intentionally unimportable adapter module."""

    _Write(project_root / "fuzzyroutines/__init__.py", "__all__ = []\n")
    _Write(project_root / "fuzzyroutines/_adapter.py", source)
    facade_source = imports or "from fuzzyroutines._adapter import Visible, Function\n"

    if mode == "authored":
        facade_source = source

    _Write(project_root / "fuzzyroutines/facade.py", facade_source)
    _Write(project_root / "docs/site/content/en/api.md", "# API\n\n::: fuzzyroutines.facade\n")
    _Write(project_root / "docs/site/api-coverage.toml", f'''schemaVersion = 1

[[surfaces]]
module = "fuzzyroutines"
source = "fuzzyroutines/__init__.py"
mode = "exports"

[[surfaces]]
module = "fuzzyroutines.facade"
source = "fuzzyroutines/facade.py"
mode = "{mode}"

[[exclusions]]
symbol = "fuzzyroutines._adapter"
reason = "Internal adapters are documented through their public facade aliases."
''')

    return {
        "contentRoot": "docs/site/content",
        "apiCoverageManifest": "docs/site/api-coverage.toml",
        "packageNames": ["fuzzyroutines"],
    }


def test_ExtractionPreservesFacadeSymbolMemberIdsAndHashes(tmp_path):
    """Move implementation sources without resetting unchanged translation contracts."""

    manifest = _Prepare(tmp_path, mode="authored")
    before = DiscoverCanonicalUnits(tmp_path, manifest)
    _Prepare(tmp_path)
    after = DiscoverCanonicalUnits(tmp_path, manifest)
    before_symbols = {unit.identifier: CanonicalHash(unit) for unit in before if unit.kind == "symbol"}
    after_symbols = {unit.identifier: CanonicalHash(unit) for unit in after if unit.kind == "symbol"}

    assert after_symbols == before_symbols
    assert "symbol:fuzzyroutines.facade.Visible.Evaluate" in after_symbols
    assert all(unit.sourcePath == "fuzzyroutines/_adapter.py" for unit in after if unit.kind == "symbol")
    assert ValidateCoverage(projectRoot=tmp_path) == ()


def test_ExplicitRenamedAliasesIncludeOnlySelectedContracts(tmp_path):
    """Follow renamed class aliases and exclude unselected authored definitions."""

    manifest = _Prepare(tmp_path, imports="from fuzzyroutines._adapter import Visible as Renamed\n")
    units = DiscoverCanonicalUnits(tmp_path, manifest)
    symbols = {unit.identifier for unit in units if unit.kind == "symbol"}

    assert symbols == {
        "symbol:fuzzyroutines.facade.Renamed",
        "symbol:fuzzyroutines.facade.Renamed.Evaluate",
    }
    assert ValidateCoverage(projectRoot=tmp_path) == ()


def test_MissingAdapterMemberDocstringRemainsACoverageFailure(tmp_path):
    """Keep adapter extraction from hiding missing public member documentation."""

    _Prepare(tmp_path, source=AUTHORED_SOURCE.replace('        """Return the supplied grade."""\n', ""))
    violations = ValidateCoverage(projectRoot=tmp_path)

    assert any("fuzzyroutines.facade.Visible.Evaluate has no source docstring" in error for error in violations)
    assert any("fuzzyroutines/_adapter.py:" in error for error in violations)


@pytest.mark.parametrize("imports, diagnostic", [
    ("from fuzzyroutines._adapter import *\n", "must name explicit symbols"),
    ("from fuzzyroutines._adapter import Missing\n", "cannot find public definition Missing"),
    ("from fuzzyroutines._adapter import Visible, Visible\n", "duplicate adapter export Visible"),
    ("from ._adapter import Visible\n", "must use absolute module paths"),
    ("from fuzzyroutines._adapter import Visible as _Hidden\n", "has no explicit public definitions"),
])
def test_UnresolvableAdapterContractsFailClosed(tmp_path, imports, diagnostic):
    """Reject ambiguous or absent facade contracts instead of losing coverage."""

    manifest = _Prepare(tmp_path, imports=imports)

    with pytest.raises(ValueError, match=diagnostic):
        DiscoverCanonicalUnits(tmp_path, manifest)

    assert any(diagnostic in error for error in ValidateCoverage(projectRoot=tmp_path))
