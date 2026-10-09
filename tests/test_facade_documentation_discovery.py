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


def _Prepare(projectRoot, mode="adapters", imports=None, source=AUTHORED_SOURCE):
    """Prepare a facade and an intentionally unimportable adapter module."""

    _Write(projectRoot / "fuzzyroutines/__init__.py", "__all__ = []\n")
    _Write(projectRoot / "fuzzyroutines/_adapter.py", source)
    facadeSource = imports or "from fuzzyroutines._adapter import Visible, Function\n"

    if mode == "authored":
        facadeSource = source

    _Write(projectRoot / "fuzzyroutines/facade.py", facadeSource)
    _Write(projectRoot / "docs/site/content/en/api.md", "# API\n\n::: fuzzyroutines.facade\n")
    _Write(projectRoot / "docs/site/api-coverage.toml", f'''schemaVersion = 1

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


def test_ExtractionPreservesFacadeSymbolMemberIdsAndHashes(tmpPath):
    """Move implementation sources without resetting unchanged translation contracts."""

    manifest = _Prepare(tmpPath, mode="authored")
    before = DiscoverCanonicalUnits(tmpPath, manifest)
    _Prepare(tmpPath)
    after = DiscoverCanonicalUnits(tmpPath, manifest)
    beforeSymbols = {unit.identifier: CanonicalHash(unit) for unit in before if unit.kind == "symbol"}
    afterSymbols = {unit.identifier: CanonicalHash(unit) for unit in after if unit.kind == "symbol"}

    assert afterSymbols == beforeSymbols
    assert "symbol:fuzzyroutines.facade.Visible.Evaluate" in afterSymbols
    assert all(unit.sourcePath == "fuzzyroutines/_adapter.py" for unit in after if unit.kind == "symbol")
    assert ValidateCoverage(projectRoot=tmpPath) == ()


def test_ExplicitRenamedAliasesIncludeOnlySelectedContracts(tmpPath):
    """Follow renamed class aliases and exclude unselected authored definitions."""

    manifest = _Prepare(tmpPath, imports="from fuzzyroutines._adapter import Visible as Renamed\n")
    units = DiscoverCanonicalUnits(tmpPath, manifest)
    symbols = {unit.identifier for unit in units if unit.kind == "symbol"}

    assert symbols == {
        "symbol:fuzzyroutines.facade.Renamed",
        "symbol:fuzzyroutines.facade.Renamed.Evaluate",
    }
    assert ValidateCoverage(projectRoot=tmpPath) == ()


def test_MissingAdapterMemberDocstringRemainsACoverageFailure(tmpPath):
    """Keep adapter extraction from hiding missing public member documentation."""

    _Prepare(tmpPath, source=AUTHORED_SOURCE.replace('        """Return the supplied grade."""\n', ""))
    violations = ValidateCoverage(projectRoot=tmpPath)

    assert any("fuzzyroutines.facade.Visible.Evaluate has no source docstring" in error for error in violations)
    assert any("fuzzyroutines/_adapter.py:" in error for error in violations)


@pytest.mark.parametrize('imports,diagnostic', [
    ("from fuzzyroutines._adapter import *\n", "must name explicit symbols"),
    ("from fuzzyroutines._adapter import Missing\n", "cannot find public definition Missing"),
    ("from fuzzyroutines._adapter import Visible, Visible\n", "duplicate adapter export Visible"),
    ("from ._adapter import Visible\n", "must use absolute module paths"),
    ("from fuzzyroutines._adapter import Visible as _Hidden\n", "has no explicit public definitions"),
])
def test_UnresolvableAdapterContractsFailClosed(tmpPath, imports, diagnostic):
    """Reject ambiguous or absent facade contracts instead of losing coverage."""

    manifest = _Prepare(tmpPath, imports=imports)

    with pytest.raises(ValueError, match=diagnostic):
        DiscoverCanonicalUnits(tmpPath, manifest)

    assert any(diagnostic in error for error in ValidateCoverage(projectRoot=tmpPath))
