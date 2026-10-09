# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Validate multilingual documentation identity, review state, and source drift.

The validator reads only tracked UTF-8 source and TOML metadata. It never
imports FuzzyRoutines, accesses the network, changes review state, or treats a
generated site as canonical documentation.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECTROOT = Path(__file__).resolve().parents[1]
PROJECTMANIFEST = PROJECTROOT / "docs" / "i18n" / "project.toml"
HASHSCHEME = "fuzzy-doc-unit-v1"
HASHFORMAT = re.compile(r"^sha256:[0-9a-f]{64}$")
PAGEIDFORMAT = re.compile(r"^page:[a-z0-9]+(?:[.-][a-z0-9]+)*$")
SYMBOLIDFORMAT = re.compile(
    r"^symbol:[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+$"
)
CONCEPTIDFORMAT = re.compile(
    r"^concept:[a-z0-9]+(?:[.-][a-z0-9]+)*$"
)
LOCALEFORMAT = re.compile(r"^[a-z]{2,3}(?:-[A-Z][A-Za-z0-9]{1,7})?$")
TRANSLATIONSTATES = frozenset(
    {"missing", "draft", "review", "approved", "stale", "retired"}
)
REVIEWCLASSES = frozenset({"editorial", "technical", "mathematical"})
REVIEWROLES = {
    "editorial": frozenset({"editorial"}),
    "technical": frozenset({"editorial", "technical"}),
    "mathematical": frozenset({"editorial", "mathematical"}),
}


@dataclass(frozen=True)
class CanonicalUnit:
    """Canonical English page or Python symbol discovered without imports.

    Attributes:
        identifier: Stable manifest identifier.
        kind: Unit kind, either `page` or `symbol`.
        sourcePath: Project-relative canonical source path.
        signature: Public symbol signature, or an empty string for a page.
        body: Canonical English Markdown page or Python docstring.
    """

    identifier: str
    kind: str
    sourcePath: str
    signature: str
    body: str


@dataclass(frozen=True)
class ValidationReport:
    """Deterministic multilingual-validation result and computed states.

    Attributes:
        diagnostics: Sorted actionable contract violations.
        states: Computed translation state keyed by unit ID and locale.
    """

    diagnostics: tuple[str, ...]
    states: dict[str, dict[str, str]]


def _Relative(path: Path, projectRoot: Path) -> str:
    """Return a stable project-relative diagnostic path."""

    try:
        return path.resolve().relative_to(projectRoot.resolve()).as_posix()

    except ValueError:
        return path.as_posix()


def _ReadCanonicalText(path: Path) -> str:
    """Read UTF-8 text, reject a byte-order mark, and normalize newlines."""

    content = path.read_bytes()

    if content.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{path}: UTF-8 byte-order marks are not allowed")

    return content.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def CanonicalHash(unit: CanonicalUnit) -> str:
    """Return the versioned SHA-256 digest for one canonical English unit."""

    signatureBytes = unit.signature.encode()
    bodyBytes = unit.body.encode()
    payload = (
        f"{HASHSCHEME}\n"
        f"id:{unit.identifier}\n"
        f"kind:{unit.kind}\n"
        f"signature-length:{len(signatureBytes)}\n"
    ).encode()
    payload += signatureBytes
    payload += f"\nbody-length:{len(bodyBytes)}\n".encode()
    payload += bodyBytes

    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _PageIdentifier(path: Path, contentRoot: Path) -> str:
    """Derive the default stable page ID for a newly discovered English page."""

    relativePath = path.relative_to(contentRoot).with_suffix("")
    parts = list(relativePath.parts)

    if parts[-1] == "index":
        parts.pop()

    return "page:" + (".".join(parts) if parts else "index")


def _FunctionSignature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Return a stable public function or method signature from syntax."""

    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    signature = f"{prefix} {node.name}({ast.unparse(node.args)})"

    if node.returns is not None:
        signature += f" -> {ast.unparse(node.returns)}"

    return signature


def _ClassSignature(node: ast.ClassDef) -> str:
    """Return a stable public class signature from syntax."""

    arguments = [ast.unparse(base) for base in node.bases]
    arguments.extend(
        f"{keyword.arg}={ast.unparse(keyword.value)}"
        for keyword in node.keywords
        if keyword.arg is not None
    )
    suffix = f"({', '.join(arguments)})" if arguments else ""
    publicFields = []

    for member in node.body:
        if (
            isinstance(member, ast.AnnAssign)
            and isinstance(member.target, ast.Name)
            and not member.target.id.startswith("_")
        ):
            field = f"{member.target.id}: {ast.unparse(member.annotation)}"

            if member.value is not None:
                field += f" = {ast.unparse(member.value)}"

            publicFields.append(field)

        elif isinstance(member, ast.Assign):
            for target in member.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    publicFields.append(f"{target.id} = {ast.unparse(member.value)}")

    fields = f"; public-fields: {'; '.join(publicFields)}" if publicFields else ""

    return f"class {node.name}{suffix}{fields}"


def _IsPropertySetter(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a method only supplies a property setter or deleter."""

    return any(
        isinstance(decorator, ast.Attribute)
        and decorator.attr in {"setter", "deleter"}
        for decorator in node.decorator_list
    )


def _IsOverload(node: ast.AST) -> bool:
    """Identify typing overload declarations without executing their module."""

    return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
        isinstance(decorator, ast.Name) and decorator.id == "overload"
        or isinstance(decorator, ast.Attribute) and decorator.attr == "overload"
        for decorator in node.decorator_list
    )


def _SourceFunctionSignature(
    path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    """Hash overload declarations and the implementation in their own scope."""

    syntax = ast.parse(_ReadCanonicalText(path), filename=str(path))

    for scope in ast.walk(syntax):
        if not isinstance(scope, (ast.Module, ast.ClassDef)):
            continue

        if not any(member.lineno == node.lineno for member in scope.body):
            continue

        signatures = [
            _FunctionSignature(member)
            for member in scope.body
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            and member.name == node.name
            and (_IsOverload(member) or member.lineno == node.lineno)
        ]

        return "\n".join(signatures)

    return _FunctionSignature(node)


def _NodeUnit(
    identifier: str,
    sourcePath: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.TypeAlias,
    sourceFilePath: Path,
) -> CanonicalUnit:
    """Build one canonical symbol unit from an authored syntax node."""

    signature = ast.unparse(node) if isinstance(node, ast.TypeAlias) else (
        _ClassSignature(node)
        if isinstance(node, ast.ClassDef)
        else _SourceFunctionSignature(sourceFilePath, node)
    )

    return CanonicalUnit(
        identifier=identifier,
        kind="symbol",
        sourcePath=sourcePath,
        signature=signature,
        body=_SourceDocstring(sourceFilePath, node),
    )


def _SourceDocstring(path: Path, node: ast.AST) -> str:
    """Read authored documentation, including the string following a type alias.

    PEP 695 aliases have no runtime per-alias docstring. The immediately following
    source string is their canonical contract, as for documented attributes.
    """

    if not isinstance(node, ast.TypeAlias):
        return ast.get_docstring(node, clean=False) or ""

    syntax = ast.parse(_ReadCanonicalText(path), filename=str(path))

    for index, statement in enumerate(syntax.body[:-1]):
        if statement.lineno != node.lineno:
            continue

        following = syntax.body[index + 1]

        if (
            isinstance(following, ast.Expr)
            and isinstance(following.value, ast.Constant)
            and isinstance(following.value.value, str)
        ):
            return following.value.value

    return ""


def _FindModulePath(moduleName: str, projectRoot: Path) -> Path:
    """Resolve a project-owned module path without importing the package."""

    relativePath = Path(*moduleName.split("."))
    modulePath = projectRoot / relativePath.with_suffix(".py")

    if modulePath.is_file():
        return modulePath

    packagePath = projectRoot / relativePath / "__init__.py"

    if packagePath.is_file():
        return packagePath

    raise ValueError(f"cannot resolve project module {moduleName}")


def _FindTopLevelNode(path: Path, name: str):
    """Return one named top-level public definition from a Python source."""

    syntax = ast.parse(_ReadCanonicalText(path), filename=str(path))

    for node in syntax.body:
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ) and node.name == name and not _IsOverload(node):
            return node

        if isinstance(node, ast.TypeAlias) and node.name.id == name:
            return node

    raise ValueError(f"{path}: cannot find public definition {name}")


def _AuthoredUnits(
    moduleName: str,
    sourcePath: Path,
    projectRoot: Path,
) -> tuple[CanonicalUnit, ...]:
    """Return public authored definitions and class members as symbol units."""

    relativePath = _Relative(sourcePath, projectRoot)
    syntax = ast.parse(_ReadCanonicalText(sourcePath), filename=str(sourcePath))
    units = []

    for node in syntax.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.TypeAlias)):
            continue

        nodeName = node.name.id if isinstance(node, ast.TypeAlias) else node.name

        if nodeName.startswith("_") or _IsOverload(node):
            continue

        symbolName = f"{moduleName}.{nodeName}"
        units.append(_NodeUnit(f"symbol:{symbolName}", relativePath, node, sourcePath))

        if not isinstance(node, ast.ClassDef):
            continue

        seenMembers = set()

        for member in node.body:
            if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if (
                member.name.startswith("_")
                or member.name in seenMembers
                or _IsPropertySetter(member)
                or _IsOverload(member)
            ):
                continue

            seenMembers.add(member.name)
            units.append(
                _NodeUnit(
                    f"symbol:{symbolName}.{member.name}",
                    relativePath,
                    member,
                    sourcePath,
                )
            )

    return tuple(units)


def _LiteralExports(syntax: ast.Module, sourcePath: Path) -> tuple[str, ...]:
    """Return the literal package export contract from `__all__`."""

    for node in syntax.body:
        if not isinstance(node, ast.Assign):
            continue

        if not any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        ):
            continue

        exports = ast.literal_eval(node.value)

        if not isinstance(exports, (list, tuple)) or not all(
            isinstance(name, str) for name in exports
        ):
            raise ValueError(f"{sourcePath}: __all__ must be a literal string sequence")

        if len(exports) != len(set(exports)):
            raise ValueError(f"{sourcePath}: __all__ contains duplicate names")

        return tuple(exports)

    raise ValueError(f"{sourcePath}: missing literal __all__")


def _ExportUnits(
    moduleName: str,
    sourcePath: Path,
    projectRoot: Path,
) -> tuple[CanonicalUnit, ...]:
    """Return root-package aliases bound to their authored English contracts."""

    syntax = ast.parse(_ReadCanonicalText(sourcePath), filename=str(sourcePath))
    exportTargets = {}

    for node in syntax.body:
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue

        for importedName in node.names:
            publicName = importedName.asname or importedName.name
            exportTargets[publicName] = (node.module, importedName.name)

    units = []

    for publicName in _LiteralExports(syntax, sourcePath):
        if publicName not in exportTargets:
            raise ValueError(f"{sourcePath}: export {publicName} has no static import target")

        targetModule, targetName = exportTargets[publicName]
        targetPath = _FindModulePath(targetModule, projectRoot)
        targetNode = _FindTopLevelNode(targetPath, targetName)
        units.append(
            _NodeUnit(
                f"symbol:{moduleName}.{publicName}",
                _Relative(targetPath, projectRoot),
                targetNode,
                targetPath,
            )
        )

    return tuple(units)


def _AdapterTargets(
    moduleName: str,
    sourceFilePath: Path,
    projectRoot: Path,
) -> tuple[tuple[str, str, Path], ...]:
    """Resolve explicit project-owned facade imports without importing code."""

    syntax = ast.parse(_ReadCanonicalText(sourceFilePath), filename=str(sourceFilePath))
    packageName = moduleName.partition(".")[0]
    targets = {}

    for node in syntax.body:
        if not isinstance(node, ast.ImportFrom):
            continue

        if node.level:
            raise ValueError(f"{sourceFilePath}: adapter imports must use absolute module paths")

        if not node.module or not node.module.startswith(packageName + "."):
            continue

        for importedName in node.names:
            publicName = importedName.asname or importedName.name

            if publicName == "*":
                raise ValueError(f"{sourceFilePath}: adapter imports must name explicit symbols")

            if publicName.startswith("_"):
                continue

            if publicName in targets:
                raise ValueError(f"{sourceFilePath}: duplicate adapter export {publicName}")

            targetPath = _FindModulePath(node.module, projectRoot)
            _FindTopLevelNode(targetPath, importedName.name)
            targets[publicName] = (publicName, importedName.name, targetPath)

    if not targets:
        raise ValueError(f"{sourceFilePath}: adapter surface has no explicit public definitions")

    return tuple(targets.values())


def _AdapterUnits(
    moduleName: str,
    sourceFilePath: Path,
    projectRoot: Path,
) -> tuple[CanonicalUnit, ...]:
    """Keep facade symbol and member identities attached to adapter source."""

    units = []

    for publicName, targetName, targetPath in _AdapterTargets(
        moduleName, sourceFilePath, projectRoot,
    ):
        sourcePrefix = f"symbol:{moduleName}.{targetName}"
        publicPrefix = f"symbol:{moduleName}.{publicName}"

        for unit in _AuthoredUnits(moduleName, targetPath, projectRoot):
            if unit.identifier == sourcePrefix or unit.identifier.startswith(sourcePrefix + "."):
                units.append(CanonicalUnit(
                    identifier=publicPrefix + unit.identifier[len(sourcePrefix):],
                    kind=unit.kind,
                    sourcePath=unit.sourcePath,
                    signature=unit.signature,
                    body=unit.body,
                ))

    return tuple(units)


def DiscoverCanonicalUnits(
    projectRoot: Path,
    projectManifest: dict,
    knownPageIds: dict[str, str] | None = None,
) -> tuple[CanonicalUnit, ...]:
    """Discover every active canonical English page and public API symbol."""

    contentRoot = projectRoot / projectManifest["contentRoot"] / "en"
    knownPageIds = knownPageIds or {}
    units = []

    for pagePath in sorted(contentRoot.rglob("*.md")):
        relativePath = _Relative(pagePath, projectRoot)
        units.append(
            CanonicalUnit(
                identifier=knownPageIds.get(
                    relativePath,
                    _PageIdentifier(pagePath, contentRoot),
                ),
                kind="page",
                sourcePath=relativePath,
                signature="",
                body=_ReadCanonicalText(pagePath),
            )
        )

    coveragePath = projectRoot / projectManifest["apiCoverageManifest"]
    coverage = tomllib.loads(_ReadCanonicalText(coveragePath))
    exclusions = {
        exclusion.get("symbol") for exclusion in coverage.get("exclusions", ())
    }

    for surface in coverage.get("surfaces", ()):
        moduleName = surface.get("module", "")
        sourcePath = projectRoot / surface.get("source", "")
        mode = surface.get("mode", "")
        packageName = moduleName.partition(".")[0]

        if packageName not in projectManifest["packageNames"]:
            raise ValueError(
                f"{coveragePath}: module {moduleName!r} is outside declared "
                f"packageNames {projectManifest['packageNames']!r}"
            )

        if mode == "authored":
            surfaceUnits = _AuthoredUnits(moduleName, sourcePath, projectRoot)

        elif mode == "exports":
            surfaceUnits = _ExportUnits(moduleName, sourcePath, projectRoot)

        elif mode == "adapters":
            surfaceUnits = _AdapterUnits(moduleName, sourcePath, projectRoot)

        else:
            raise ValueError(f"{coveragePath}: invalid surface mode {mode!r}")

        units.extend(
            unit
            for unit in surfaceUnits
            if unit.identifier.removeprefix("symbol:") not in exclusions
        )

    identifiers = [unit.identifier for unit in units]

    if len(identifiers) != len(set(identifiers)):
        duplicateIds = sorted(
            identifier
            for identifier in set(identifiers)
            if identifiers.count(identifier) > 1
        )
        raise ValueError(f"duplicate discovered unit IDs: {', '.join(duplicateIds)}")

    return tuple(sorted(units, key=lambda unit: unit.identifier))


def _LoadProjectManifest(path: Path) -> dict:
    """Load and validate the reusable multilingual project manifest."""

    manifest = tomllib.loads(_ReadCanonicalText(path))

    if manifest.get("schemaVersion") != 1:
        raise ValueError(f"{path}: schemaVersion must be 1")

    requiredText = (
        "projectId",
        "projectName",
        "sourceLocale",
        "contentRoot",
        "unitManifest",
        "buildRoot",
        "apiCoverageManifest",
        "publicationPath",
    )

    for fieldName in requiredText:
        if not isinstance(manifest.get(fieldName), str) or not manifest[fieldName]:
            raise ValueError(f"{path}: {fieldName} must be a non-empty string")

    locales = manifest.get("locales")

    if manifest["sourceLocale"] != "en":
        raise ValueError(f"{path}: sourceLocale must be 'en'")

    if (
        not isinstance(locales, list)
        or len(locales) < 2
        or locales[0] != manifest["sourceLocale"]
        or len(locales) != len(set(locales))
        or not all(isinstance(locale, str) and LOCALEFORMAT.fullmatch(locale) for locale in locales)
    ):
        raise ValueError(
            f"{path}: locales must be a unique list beginning with sourceLocale "
            "and containing at least one target locale"
        )

    packageNames = manifest.get("packageNames")

    if (
        not isinstance(packageNames, list)
        or not packageNames
        or not all(isinstance(name, str) and name.strip() for name in packageNames)
    ):
        raise ValueError(f"{path}: packageNames must be a non-empty string list")

    publicationPath = manifest["publicationPath"]

    if (
        not publicationPath.startswith("/")
        or (publicationPath != "/" and publicationPath.endswith("/"))
        or ".." in Path(publicationPath).parts
    ):
        raise ValueError(
            f"{path}: publicationPath must be an absolute URL path without a trailing slash"
        )

    branding = manifest.get("branding")

    if not isinstance(branding, dict):
        raise TypeError(f"{path}: branding must be a table")

    for fieldName in ("organization", "assetRoot"):
        if not isinstance(branding.get(fieldName), str) or not branding[fieldName].strip():
            raise ValueError(f"{path}: branding.{fieldName} must be a non-empty string")

    glossaries = manifest.get("glossaries", {})

    targetLocales = set(locales[1:])

    if set(glossaries) != targetLocales:
        raise ValueError(
            f"{path}: glossaries must match target locales "
            f"{', '.join(sorted(targetLocales))}"
        )

    return manifest


def _ValidTimestamp(value) -> bool:
    """Return whether a value is a timezone-aware ISO-8601 timestamp."""

    if not isinstance(value, str) or not value.endswith("Z"):
        return False

    try:
        parsedValue = datetime.fromisoformat(value)

    except ValueError:
        return False

    return parsedValue.utcoffset() is not None


def _ValidateGlossaries(
    projectRoot: Path,
    projectManifest: dict,
) -> tuple[str, ...]:
    """Return deterministic cross-locale glossary integrity violations."""

    diagnostics = []
    conceptSets = {}
    englishTerms = {}

    targetLocales = tuple(projectManifest["locales"][1:])

    for locale in targetLocales:
        glossaryPath = projectRoot / projectManifest["glossaries"][locale]
        glossaryLabel = _Relative(glossaryPath, projectRoot)

        try:
            glossary = tomllib.loads(_ReadCanonicalText(glossaryPath))

        except (OSError, UnicodeError, ValueError, tomllib.TOMLDecodeError) as error:
            diagnostics.append(f"{glossaryLabel}: cannot load glossary: {error}")
            continue

        if glossary.get("schemaVersion") != 1:
            diagnostics.append(f"{glossaryLabel}: schemaVersion must be 1")

        if glossary.get("locale") != locale:
            diagnostics.append(f"{glossaryLabel}: locale must be {locale}")

        conceptIds = []

        for index, term in enumerate(glossary.get("terms", ())):
            termLabel = f"{glossaryLabel}:terms[{index}]"
            identifier = term.get("id", "")
            english = term.get("english", "")
            preferred = term.get("preferred", "")
            avoid = term.get("avoid", ())
            references = term.get("references", ())

            if not CONCEPTIDFORMAT.fullmatch(identifier):
                diagnostics.append(f"{termLabel}: invalid concept ID {identifier!r}")

            conceptIds.append(identifier)

            if not isinstance(english, str) or not english.strip():
                diagnostics.append(f"{termLabel}: english must be non-empty")

            if not isinstance(preferred, str) or not preferred.strip():
                diagnostics.append(f"{termLabel}: preferred must be non-empty")

            if not isinstance(avoid, list) or not all(
                isinstance(value, str) and value.strip() for value in avoid
            ):
                diagnostics.append(f"{termLabel}: avoid must be a string list")

            elif preferred in avoid:
                diagnostics.append(f"{termLabel}: preferred term cannot be prohibited")

            if not isinstance(references, list) or not references:
                diagnostics.append(f"{termLabel}: at least one reference is required")

            else:
                for reference in references:
                    referencePath = projectRoot / reference

                    if not isinstance(reference, str) or not referencePath.is_file():
                        diagnostics.append(
                            f"{termLabel}: missing reference {reference!r}"
                        )

            if identifier in englishTerms and englishTerms[identifier] != english:
                diagnostics.append(
                    f"{termLabel}: canonical English term differs across locales"
                )

            englishTerms[identifier] = english

        if len(conceptIds) != len(set(conceptIds)):
            diagnostics.append(f"{glossaryLabel}: duplicate concept IDs")

        conceptSets[locale] = frozenset(conceptIds)

    if len(conceptSets) == len(targetLocales) and len(set(conceptSets.values())) > 1:
        diagnostics.append("docs/i18n/glossaries: target locale concept IDs must match")

    return tuple(diagnostics)


def _TranslationDiagnostic(
    unitId: str,
    locale: str,
    sourcePath: str,
    translationPath: str,
    expectedHash: str,
    actualHash: str,
    action: str,
) -> str:
    """Format one complete stale-translation diagnostic."""

    return (
        f"unit={unitId} locale={locale} source={sourcePath} "
        f"translation={translationPath or '<missing>'} "
        f"expected={expectedHash or '<missing>'} actual={actualHash} "
        f"action={action}"
    )


def ValidateLocales(
    projectRoot: Path = PROJECTROOT,
    projectManifestPath: Path | None = None,
) -> ValidationReport:
    """Validate canonical inventory, source hashes, review state, and glossaries."""

    projectManifestPath = projectManifestPath or projectRoot / "docs" / "i18n" / "project.toml"
    diagnostics = []
    states = {}

    try:
        projectManifest = _LoadProjectManifest(projectManifestPath)
        targetLocales = tuple(projectManifest["locales"][1:])
        unitManifestPath = projectRoot / projectManifest["unitManifest"]
        unitManifest = tomllib.loads(_ReadCanonicalText(unitManifestPath))
        knownPageIds = {
            record.get("sourcePath", ""): record.get("id", "")
            for record in unitManifest.get("units", ())
            if record.get("kind") == "page"
        }
        discoveredUnits = DiscoverCanonicalUnits(
            projectRoot,
            projectManifest,
            knownPageIds,
        )

    except (
        OSError,
        UnicodeError,
        TypeError,
        ValueError,
        SyntaxError,
        tomllib.TOMLDecodeError,
    ) as error:
        return ValidationReport((str(error),), {})

    unitManifestLabel = _Relative(unitManifestPath, projectRoot)

    if unitManifest.get("schemaVersion") != 1:
        diagnostics.append(f"{unitManifestLabel}: schemaVersion must be 1")

    discoveredById = {unit.identifier: unit for unit in discoveredUnits}
    records = unitManifest.get("units", ())
    recordsById = {}
    activeSourcePaths = {}

    for index, record in enumerate(records):
        identifier = record.get("id", "")
        recordLabel = f"{unitManifestLabel}:units[{index}]"

        if identifier in recordsById:
            diagnostics.append(f"{recordLabel}: duplicate unit ID {identifier}")

        recordsById[identifier] = record

        if record.get("kind") == "page":
            sourcePath = record.get("sourcePath", "")
            priorId = activeSourcePaths.get(sourcePath)

            if priorId:
                diagnostics.append(
                    f"{recordLabel}: sourcePath {sourcePath!r} is already owned by {priorId}"
                )

            activeSourcePaths[sourcePath] = identifier

    missingIds = sorted(set(discoveredById) - set(recordsById))
    unexpectedIds = sorted(set(recordsById) - set(discoveredById))

    for identifier in missingIds:
        unit = discoveredById[identifier]
        diagnostics.append(
            f"{unitManifestLabel}: missing canonical unit {identifier} "
            f"source={unit.sourcePath} action=add exactly one manifest record"
        )

    for identifier in unexpectedIds:
        diagnostics.append(
            f"{unitManifestLabel}: unknown or retired-unmarked unit {identifier} "
            "action=remove it or implement an explicit retired-unit contract"
        )

    for identifier in sorted(set(discoveredById) & set(recordsById)):
        unit = discoveredById[identifier]
        record = recordsById[identifier]
        recordLabel = f"{unitManifestLabel}:{identifier}"
        currentHash = CanonicalHash(unit)
        recordedHash = record.get("sourceHash", "")
        sourcePath = record.get("sourcePath", "")
        reviewClass = record.get("reviewClass", "")

        identifierFormat = PAGEIDFORMAT if unit.kind == "page" else SYMBOLIDFORMAT

        if not identifierFormat.fullmatch(identifier):
            diagnostics.append(f"{recordLabel}: invalid stable ID")

        if record.get("kind") != unit.kind:
            diagnostics.append(f"{recordLabel}: kind must be {unit.kind}")

        if sourcePath != unit.sourcePath:
            diagnostics.append(
                f"{recordLabel}: sourcePath={sourcePath!r} actual={unit.sourcePath!r} "
                "action=preserve the stable ID and update its canonical source path"
            )

        if not HASHFORMAT.fullmatch(recordedHash):
            diagnostics.append(f"{recordLabel}: invalid sourceHash {recordedHash!r}")

        elif recordedHash != currentHash:
            diagnostics.append(
                f"{recordLabel}: canonical source drift expected={recordedHash} "
                f"actual={currentHash} source={unit.sourcePath} "
                "action=review the English change and refresh sourceHash"
            )

        if reviewClass not in REVIEWCLASSES:
            diagnostics.append(f"{recordLabel}: invalid reviewClass {reviewClass!r}")

        translations = record.get("translations", {})
        unexpectedLocales = sorted(set(translations) - set(targetLocales))

        for locale in unexpectedLocales:
            diagnostics.append(f"{recordLabel}: unsupported locale {locale}")

        states[identifier] = {}

        for locale in targetLocales:
            translation = translations.get(locale)

            if not isinstance(translation, dict):
                diagnostics.append(f"{recordLabel}: missing {locale} translation state")
                states[identifier][locale] = "invalid"
                continue

            state = translation.get("state", "")
            translationPath = translation.get("path", "")
            reviews = translation.get("reviews", ())

            if state not in TRANSLATIONSTATES:
                diagnostics.append(f"{recordLabel}: invalid {locale} state {state!r}")
                states[identifier][locale] = "invalid"
                continue

            states[identifier][locale] = state

            if state == "missing":
                if translationPath or reviews:
                    diagnostics.append(
                        f"{recordLabel}: {locale} missing state cannot carry a path or reviews"
                    )

                continue

            if state == "retired":
                diagnostics.append(
                    f"{recordLabel}: active canonical unit cannot have retired {locale} state"
                )
                continue

            resolvedTranslation = projectRoot / translationPath

            if not translationPath or not resolvedTranslation.is_file():
                diagnostics.append(
                    _TranslationDiagnostic(
                        identifier,
                        locale,
                        unit.sourcePath,
                        translationPath,
                        recordedHash,
                        currentHash,
                        "add the locale file or use state=missing",
                    )
                )

            if state != "approved":
                continue

            requiredRoles = REVIEWROLES.get(reviewClass, frozenset())
            reviewedRoles = set()
            mismatchedReviewHash = False

            if not isinstance(reviews, list):
                diagnostics.append(f"{recordLabel}: {locale} reviews must be a list")
                reviews = ()

            for reviewIndex, review in enumerate(reviews):
                reviewLabel = f"{recordLabel}:{locale}:reviews[{reviewIndex}]"
                role = review.get("role", "")
                reviewHash = review.get("reviewedSourceHash", "")

                if role in reviewedRoles:
                    diagnostics.append(f"{reviewLabel}: duplicate review role {role}")

                reviewedRoles.add(role)

                if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
                    diagnostics.append(f"{reviewLabel}: reviewer must be non-empty")

                if not _ValidTimestamp(review.get("reviewedAt")):
                    diagnostics.append(f"{reviewLabel}: reviewedAt must be a UTC timestamp")

                if reviewHash != currentHash:
                    mismatchedReviewHash = True

            missingRoles = sorted(requiredRoles - reviewedRoles)

            if missingRoles:
                diagnostics.append(
                    f"{recordLabel}: {locale} approved state lacks review roles "
                    f"{', '.join(missingRoles)}"
                )

            if recordedHash != currentHash or mismatchedReviewHash:
                states[identifier][locale] = "stale"
                diagnostics.append(
                    _TranslationDiagnostic(
                        identifier,
                        locale,
                        unit.sourcePath,
                        translationPath,
                        recordedHash,
                        currentHash,
                        "set state=stale and obtain new accountable human reviews",
                    )
                )

    diagnostics.extend(_ValidateGlossaries(projectRoot, projectManifest))

    return ValidationReport(tuple(sorted(set(diagnostics))), states)


def _WriteReport(report: ValidationReport, outputPath: Path) -> None:
    """Write deterministic machine-readable validation evidence."""

    outputPath.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "status": "pass" if not report.diagnostics else "fail",
        "diagnostics": list(report.diagnostics),
        "states": report.states,
    }
    outputPath.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def ParseArguments(arguments=None):
    """Parse locale-documentation validator arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "inventory"))
    parser.add_argument("--project-root", dest="projectRoot", type=Path, default=PROJECTROOT)
    parser.add_argument("--project-manifest", dest="projectManifest", type=Path)
    parser.add_argument("--output", type=Path)

    return parser.parse_args(arguments)


def Main(arguments=None):
    """Run deterministic locale validation or print canonical inventory."""

    options = ParseArguments(arguments)
    projectManifestPath = options.projectManifest or (
        options.projectRoot / "docs" / "i18n" / "project.toml"
    )

    if options.command == "inventory":
        try:
            projectManifest = _LoadProjectManifest(projectManifestPath)
            unitManifestPath = options.projectRoot / projectManifest["unitManifest"]
            knownPageIds = {}

            if unitManifestPath.is_file():
                unitManifest = tomllib.loads(_ReadCanonicalText(unitManifestPath))
                knownPageIds = {
                    record.get("sourcePath", ""): record.get("id", "")
                    for record in unitManifest.get("units", ())
                    if record.get("kind") == "page"
                }

            units = DiscoverCanonicalUnits(
                options.projectRoot,
                projectManifest,
                knownPageIds,
            )

        except (
            OSError,
            UnicodeError,
            TypeError,
            ValueError,
            SyntaxError,
            tomllib.TOMLDecodeError,
        ) as error:
            print(error, file=sys.stderr)
            return 1

        for unit in units:
            print(
                json.dumps(
                    {
                        "id": unit.identifier,
                        "kind": unit.kind,
                        "sourcePath": unit.sourcePath,
                        "sourceHash": CanonicalHash(unit),
                    },
                    sort_keys=True,
                )
            )

        return 0

    report = ValidateLocales(options.projectRoot, projectManifestPath)

    if options.output:
        _WriteReport(report, options.output)

    if report.diagnostics:
        for diagnostic in report.diagnostics:
            print(diagnostic, file=sys.stderr)

        return 1

    print("Multilingual documentation validation: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
