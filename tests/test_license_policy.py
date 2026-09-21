# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Tests for repository-wide Apache-2.0 licensing invariants."""

from tools.check_license_headers import PROJECTROOT, ValidateHeader, ValidateRepository


def test_CurrentRepositoryPassesLicensePolicy():
    assert ValidateRepository() == ()


def test_PythonHeaderRequiresProjectAndApacheFields(tmp_path):
    projectRoot = tmp_path
    modulePath = projectRoot / "module.py"
    modulePath.write_text('"""Missing ownership header."""\n', encoding="utf-8")

    violations = ValidateHeader(modulePath, projectRoot)

    assert len(violations) == 4
    assert any("SPDX-License-Identifier: Apache-2.0" in violation for violation in violations)
    assert any("SPDX-FileCopyrightText:" in violation for violation in violations)
    assert any("Project: FuzzyRoutines by Fuzzy Technologies" in violation for violation in violations)
    assert any("Maintainer: Fuzzy Technologies contributors" in violation for violation in violations)


def test_HeaderRejectsConflictingLicenseIdentifier(tmp_path):
    documentPath = tmp_path / "document.md"
    documentPath.write_text(
        "<!--\n"
        "SPDX-FileCopyrightText: 2026 Fuzzy Technologies\n"
        "SPDX-License-Identifier: Apache-2.0\n"
        "SPDX-License-Identifier: MIT\n"
        "-->\n",
        encoding="utf-8",
    )

    violations = ValidateHeader(documentPath, tmp_path)

    assert violations == ("document.md: conflicting SPDX license MIT",)


def test_CanonicalLicenseAndNoticeAreTracked():
    assert (PROJECTROOT / "LICENSE").is_file()
    assert (PROJECTROOT / "NOTICE").is_file()
