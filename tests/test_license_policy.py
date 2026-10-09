# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Tests for repository-wide Apache-2.0 licensing invariants."""

from tools.check_license_headers import PROJECTROOT, ValidateHeader, ValidateRepository


def test_CurrentRepositoryPassesLicensePolicy():
    """Verify that current repository passes license policy."""

    assert ValidateRepository() == ()


def test_PythonHeaderRequiresProjectAndApacheFields(tmpPath):
    """Verify that python header requires project and apache fields."""

    projectRoot = tmpPath
    modulePath = projectRoot / "module.py"
    modulePath.write_text('"""Missing ownership header."""\n', encoding="utf-8")

    violations = ValidateHeader(modulePath, projectRoot)

    assert len(violations) == 4
    assert any("SPDX-License-Identifier: Apache-2.0" in violation for violation in violations)
    assert any("SPDX-FileCopyrightText:" in violation for violation in violations)
    assert any("Project: FuzzyRoutines by Fuzzy Technologies" in violation for violation in violations)
    assert any("Maintainer: Fuzzy Technologies contributors" in violation for violation in violations)


def test_HeaderRejectsConflictingLicenseIdentifier(tmpPath):
    """Verify that header rejects conflicting license identifier."""

    documentPath = tmpPath / "document.md"
    documentPath.write_text(
        "<!--\n"
        "SPDX-FileCopyrightText: 2026 Fuzzy Technologies\n"
        "SPDX-License-Identifier: Apache-2.0\n"
        "SPDX-License-Identifier: MIT\n"
        "-->\n",
        encoding="utf-8",
    )

    violations = ValidateHeader(documentPath, tmpPath)

    assert violations == ("document.md: conflicting SPDX license MIT",)


def test_CanonicalLicenseAndNoticeAreTracked():
    """Verify that canonical license and notice are tracked."""

    assert (PROJECTROOT / "LICENSE").is_file()
    assert (PROJECTROOT / "NOTICE").is_file()
