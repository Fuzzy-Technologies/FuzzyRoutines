# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Enforce deterministic API coverage and documentation-link contracts."""

from __future__ import annotations

import argparse
import ast
import html.parser
import re
import subprocess
import sys
import tomllib
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from tools.locale_documentation import ValidateLocales

PROJECTROOT = Path(__file__).resolve().parents[1]
MANIFESTPATH = PROJECTROOT / "docs" / "site" / "api-coverage.toml"
REFERENCEROOT = PROJECTROOT / "docs" / "site" / "content" / "en"
SITEROOT = PROJECTROOT / "_build" / "api-reference" / "site"
PACKAGEROOT = PROJECTROOT / "fuzzyroutines"
MARKDOWNLINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
EXPLICITANCHOR = re.compile(r"\s*\{#([^}]+)\}\s*$")
DIRECTIVE = re.compile(r"^:::\s+([A-Za-z_][\w.]*)\s*$")


@dataclass(frozen=True)
class _Symbol:
    """Describe one statically discovered public symbol."""

    name: str
    path: Path
    line: int


@dataclass(frozen=True)
class _Directive:
    """Describe one mkdocstrings directive and its explicit member filter."""

    module: str
    members: frozenset[str] | None
    path: Path
    line: int


class _PageParser(html.parser.HTMLParser):
    """Collect rendered anchors and navigational links from one HTML page."""

    def __init__(self):
        """Initialize empty anchor and link collections."""

        super().__init__(convert_charrefs=True)
        self.anchors = set()
        self.links = []

    def handle_starttag(self, tag, attributes):
        """Record identifiers and navigational targets from a start tag."""

        attributeMap = dict(attributes)
        identifier = attributeMap.get("id")

        if identifier:
            self.anchors.add(identifier)

        if tag == "a" and attributeMap.get("href"):
            self.links.append(attributeMap["href"])


def _Relative(path: Path, projectRoot: Path) -> str:
    """Return a stable project-relative diagnostic path."""

    try:
        return path.resolve().relative_to(projectRoot.resolve()).as_posix()

    except ValueError:
        return path.as_posix()


def _ParseSyntax(path: Path) -> ast.Module:
    """Parse one Python source file without importing it."""

    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _IsPropertySetter(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a method only supplies a property setter/deleter."""

    for decorator in node.decorator_list:
        if (
            isinstance(decorator, ast.Attribute)
            and decorator.attr in {"setter", "deleter"}
        ):
            return True

    return False


def _AuthoredSymbols(moduleName: str, path: Path) -> tuple[_Symbol, ...]:
    """Return authored public definitions and public class members."""

    syntax = _ParseSyntax(path)
    symbols = []

    for node in syntax.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        if node.name.startswith("_"):
            continue

        symbolName = f"{moduleName}.{node.name}"
        symbols.append(_Symbol(symbolName, path, node.lineno))

        if not isinstance(node, ast.ClassDef):
            continue

        seenMembers = set()

        for member in node.body:
            if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if member.name.startswith("_") or _IsPropertySetter(member):
                continue

            if member.name in seenMembers:
                continue

            seenMembers.add(member.name)
            symbols.append(
                _Symbol(f"{symbolName}.{member.name}", path, member.lineno)
            )

    return tuple(symbols)


def _LiteralExports(path: Path) -> tuple[str, ...]:
    """Return the literal package ``__all__`` contract."""

    syntax = _ParseSyntax(path)

    for node in syntax.body:
        if not isinstance(node, ast.Assign):
            continue

        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            continue

        value = ast.literal_eval(node.value)

        if not isinstance(value, (list, tuple)) or not all(
            isinstance(name, str) for name in value
        ):
            raise ValueError(f"{path}: __all__ must be a literal string sequence")

        if len(value) != len(set(value)):
            raise ValueError(f"{path}: __all__ contains duplicate names")

        return tuple(value)

    raise ValueError(f"{path}: missing literal __all__")


def _ExportSources(path: Path) -> dict[str, str]:
    """Map re-exported package names to their source modules."""

    sourceModules = {}

    for node in _ParseSyntax(path).body:
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue

        for importedName in node.names:
            publicName = importedName.asname or importedName.name
            sourceModules[publicName] = node.module

    return sourceModules


def _LoadManifest(manifestPath: Path) -> dict:
    """Load and minimally validate the versioned coverage manifest."""

    manifest = tomllib.loads(manifestPath.read_text(encoding="utf-8"))

    if manifest.get("schemaVersion") != 1:
        raise ValueError(f"{manifestPath}: schemaVersion must be 1")

    if not manifest.get("surfaces"):
        raise ValueError(f"{manifestPath}: at least one public surface is required")

    return manifest


def _ParseDirectives(referenceRoot: Path) -> tuple[_Directive, ...]:
    """Return mkdocstrings directives and explicit member selections."""

    directives = []

    for markdownPath in sorted(referenceRoot.rglob("*.md")):
        lines = markdownPath.read_text(encoding="utf-8").splitlines()

        for index, line in enumerate(lines):
            match = DIRECTIVE.match(line)

            if not match:
                continue

            members = None

            for optionIndex in range(index + 1, len(lines)):
                optionLine = lines[optionIndex]

                if optionLine and not optionLine.startswith(" "):
                    break

                stripped = optionLine.strip()

                if not stripped.startswith("members:"):
                    continue

                memberValue = stripped.partition(":")[2].strip().lower()

                if memberValue == "false":
                    members = frozenset()
                    break

                selectedMembers = []

                for memberIndex in range(optionIndex + 1, len(lines)):
                    memberLine = lines[memberIndex]

                    if not memberLine.strip():
                        continue

                    indentation = len(memberLine) - len(memberLine.lstrip())

                    if indentation <= len(optionLine) - len(optionLine.lstrip()):
                        break

                    memberMatch = re.match(r"\s*-\s+([A-Za-z_]\w*)\s*$", memberLine)

                    if memberMatch:
                        selectedMembers.append(memberMatch.group(1))

                members = frozenset(selectedMembers)
                break

            directives.append(
                _Directive(match.group(1), members, markdownPath, index + 1)
            )

    return tuple(directives)


def _IsRendered(
    symbolName: str,
    directives: tuple[_Directive, ...],
    alternativeName: str | None = None,
) -> bool:
    """Return whether a symbol is included by a tracked reference directive."""

    for candidateName in (symbolName, alternativeName):
        if not candidateName:
            continue

        for directive in directives:
            if candidateName == directive.module:
                return True

            prefix = f"{directive.module}."

            if not candidateName.startswith(prefix):
                continue

            memberName = candidateName[len(prefix):].partition(".")[0]

            if directive.members is None or memberName in directive.members:
                return True

    return False


def _ModuleName(path: Path, packageRoot: Path) -> str:
    """Return the import name for one package source file."""

    relativePath = path.relative_to(packageRoot)
    if relativePath.name == "__init__.py":
        parts = relativePath.parent.parts

    else:
        parts = relativePath.with_suffix("").parts

    suffix = ".".join(parts)

    return "fuzzyroutines" + (f".{suffix}" if suffix else "")


def ValidateCoverage(
    projectRoot: Path = PROJECTROOT,
    manifestPath: Path | None = None,
    referenceRoot: Path | None = None,
) -> tuple[str, ...]:
    """Return public API coverage and source-docstring violations."""

    manifestPath = manifestPath or projectRoot / "docs" / "site" / "api-coverage.toml"
    referenceRoot = referenceRoot or projectRoot / "docs" / "site" / "content" / "en"
    packageRoot = projectRoot / "fuzzyroutines"

    try:
        manifest = _LoadManifest(manifestPath)

    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        return (str(error),)

    errors = []
    exclusions = {}

    for exclusion in manifest.get("exclusions", ()):
        symbolName = exclusion.get("symbol", "")
        reason = exclusion.get("reason", "").strip()

        if not symbolName or len(reason) < 12:
            errors.append(
                f"{_Relative(manifestPath, projectRoot)}: exclusion {symbolName or '<missing>'} "
                "requires an actionable reason"
            )
            continue

        if symbolName in exclusions:
            errors.append(
                f"{_Relative(manifestPath, projectRoot)}: duplicate exclusion {symbolName}"
            )

        exclusions[symbolName] = reason

    directives = _ParseDirectives(referenceRoot)
    configuredModules = set()
    discoveredSymbols = set()
    exportSources = {}

    for surface in manifest["surfaces"]:
        moduleName = surface.get("module", "")
        sourceValue = surface.get("source", "")
        mode = surface.get("mode", "")
        sourcePath = projectRoot / sourceValue

        if not moduleName or mode not in {"authored", "exports"} or not sourcePath.is_file():
            errors.append(
                f"{_Relative(manifestPath, projectRoot)}: invalid surface "
                f"module={moduleName!r}, source={sourceValue!r}, mode={mode!r}"
            )
            continue

        if moduleName in configuredModules:
            errors.append(
                f"{_Relative(manifestPath, projectRoot)}: duplicate surface {moduleName}"
            )
            continue

        configuredModules.add(moduleName)

        if mode == "exports":
            try:
                exportNames = _LiteralExports(sourcePath)

            except ValueError as error:
                errors.append(str(error))
                continue

            exportSources.update(_ExportSources(sourcePath))
            symbols = tuple(
                _Symbol(f"{moduleName}.{name}", sourcePath, 1) for name in exportNames
            )

        else:
            symbols = _AuthoredSymbols(moduleName, sourcePath)

        topLevelSymbols = [
            symbol for symbol in symbols if symbol.name.count(".") == moduleName.count(".") + 1
        ]

        for symbol in symbols:
            discoveredSymbols.add(symbol.name)

            if symbol.name in exclusions:
                continue

            if mode == "authored":
                syntax = _ParseSyntax(symbol.path)
                targetName = symbol.name.rsplit(".", 1)[1]
                owningName = symbol.name[len(moduleName) + 1 :].split(".")
                targetNode = None

                for node in syntax.body:
                    if getattr(node, "name", None) != owningName[0]:
                        continue

                    targetNode = node

                    if len(owningName) == 2 and isinstance(node, ast.ClassDef):
                        targetNode = next(
                            (
                                member
                                for member in node.body
                                if getattr(member, "name", None) == targetName
                                and not _IsPropertySetter(member)
                            ),
                            None,
                        )

                    break

                if targetNode is not None and not ast.get_docstring(targetNode, clean=False):
                    errors.append(
                        f"{_Relative(symbol.path, projectRoot)}:{symbol.line}: "
                        f"{symbol.name} has no source docstring"
                    )

        for symbol in topLevelSymbols:
            if symbol.name in exclusions:
                continue

            alternativeName = None

            if mode == "exports":
                shortName = symbol.name.rsplit(".", 1)[1]
                sourceModule = exportSources.get(shortName)

                if sourceModule:
                    alternativeName = f"{sourceModule}.{shortName}"

            if not _IsRendered(symbol.name, directives, alternativeName):
                errors.append(
                    f"{_Relative(symbol.path, projectRoot)}:{symbol.line}: "
                    f"{symbol.name} is public but absent from mkdocstrings reference pages"
                )

    packageModules = {
        _ModuleName(path, packageRoot)
        for path in packageRoot.rglob("*.py")
        if "__pycache__" not in path.parts
    }

    for moduleName in sorted(packageModules - configuredModules - set(exclusions)):
        modulePath = moduleName.replace(".", "/") + ".py"
        errors.append(
            f"{modulePath}:1: public module {moduleName} is neither covered nor excluded"
        )

    for symbolName in sorted(exclusions):
        isModule = symbolName in packageModules

        if not isModule and symbolName not in discoveredSymbols:
            errors.append(
                f"{_Relative(manifestPath, projectRoot)}: stale exclusion {symbolName}"
            )

        if _IsRendered(symbolName, directives):
            errors.append(
                f"{_Relative(manifestPath, projectRoot)}: excluded symbol is rendered: {symbolName}"
            )

    return tuple(errors)


def _TrackedMarkdown(projectRoot: Path) -> tuple[Path, ...]:
    """Return tracked Markdown paths in deterministic order."""

    output = subprocess.check_output(
        ["git", "ls-files", "-z", "*.md"],
        cwd=projectRoot,
    ).decode("utf-8")
    return tuple(projectRoot / value for value in output.split("\0") if value)


def _MarkdownLines(path: Path):
    """Yield non-code Markdown lines with one-based positions."""

    inFence = False
    fenceMarker = ""

    for lineNumber, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.lstrip()

        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]

            if not inFence:
                inFence = True
                fenceMarker = marker

            elif marker == fenceMarker:
                inFence = False

            continue

        if not inFence:
            yield lineNumber, line


def _HeadingAnchors(path: Path) -> frozenset[str]:
    """Return common MkDocs-compatible heading anchors for one Markdown file."""

    anchors = set()
    counts = {}

    for _, line in _MarkdownLines(path):
        match = HEADING.match(line)

        if not match:
            continue

        headingText = match.group(2).strip().rstrip("#").strip()
        explicitMatch = EXPLICITANCHOR.search(headingText)

        if explicitMatch:
            anchors.add(explicitMatch.group(1))
            headingText = headingText[: explicitMatch.start()].strip()

        headingText = re.sub(r"`([^`]*)`", r"\1", headingText)
        headingText = re.sub(r"<[^>]+>", "", headingText)
        slug = re.sub(r"[^\w\- ]", "", headingText.lower(), flags=re.UNICODE)
        slug = re.sub(r"[\s\-]+", "-", slug).strip("-")
        count = counts.get(slug, 0)

        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}_{count}")

    return frozenset(anchors)


def _LinkTarget(rawTarget: str) -> str:
    """Remove an optional Markdown title from an inline link target."""

    target = rawTarget.strip()

    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]

    return re.split(r"\s+[\"']", target, maxsplit=1)[0]


def ValidateSourceLinks(
    projectRoot: Path = PROJECTROOT,
    markdownPaths: tuple[Path, ...] | None = None,
) -> tuple[str, ...]:
    """Return broken repository-local Markdown links and anchors."""

    markdownPaths = markdownPaths or _TrackedMarkdown(projectRoot)
    errors = []
    anchorCache = {}

    for sourcePath in markdownPaths:
        for lineNumber, line in _MarkdownLines(sourcePath):
            for match in MARKDOWNLINK.finditer(line):
                rawTarget = _LinkTarget(match.group(1))
                parsedTarget = urllib.parse.urlsplit(rawTarget)

                if parsedTarget.scheme or rawTarget.startswith("//"):
                    continue

                decodedPath = urllib.parse.unquote(parsedTarget.path)

                if decodedPath:
                    targetPath = (
                        projectRoot / decodedPath.lstrip("/")
                        if decodedPath.startswith("/")
                        else sourcePath.parent / decodedPath
                    ).resolve()

                else:
                    targetPath = sourcePath.resolve()

                try:
                    targetPath.relative_to(projectRoot.resolve())

                except ValueError:
                    errors.append(
                        f"{_Relative(sourcePath, projectRoot)}:{lineNumber}: "
                        f"local link escapes repository: {rawTarget}"
                    )
                    continue

                if not targetPath.exists():
                    errors.append(
                        f"{_Relative(sourcePath, projectRoot)}:{lineNumber}: "
                        f"missing local link target: {rawTarget}"
                    )
                    continue

                fragment = urllib.parse.unquote(parsedTarget.fragment)

                if fragment and targetPath.suffix.lower() == ".md":
                    anchors = anchorCache.setdefault(targetPath, _HeadingAnchors(targetPath))

                    if fragment not in anchors:
                        errors.append(
                            f"{_Relative(sourcePath, projectRoot)}:{lineNumber}: "
                            f"missing Markdown anchor {fragment!r} in "
                            f"{_Relative(targetPath, projectRoot)}"
                        )

    return tuple(errors)


def _RenderedSourcePath(htmlPath: Path, siteRoot: Path, referenceRoot: Path) -> Path:
    """Infer a Markdown source path from a directory-style rendered URL."""

    relativePath = htmlPath.relative_to(siteRoot)

    if relativePath == Path("index.html"):
        return referenceRoot / "index.md"

    if relativePath.name == "index.html":
        directPath = referenceRoot / relativePath.parent.with_suffix(".md")
        nestedPath = referenceRoot / relativePath.parent / "index.md"

        return directPath if directPath.is_file() else nestedPath

    inferredPath = referenceRoot / relativePath.with_suffix(".md")

    return inferredPath if inferredPath.is_file() else htmlPath


def _SiteUrlPath(projectRoot: Path) -> str:
    """Return the configured deployment path used by absolute rendered links."""

    configurationPath = projectRoot / "docs" / "site" / "mkdocs.yml"

    if not configurationPath.is_file():
        return "/"

    configurationText = configurationPath.read_text(encoding="utf-8")
    match = re.search(r"^site_url:\s*(\S+)\s*$", configurationText, re.MULTILINE)

    if not match:
        return "/"

    sitePath = urllib.parse.urlsplit(match.group(1)).path

    return sitePath.rstrip("/") + "/"


def ValidateRenderedLinks(
    siteRoot: Path = SITEROOT,
    referenceRoot: Path = REFERENCEROOT,
    projectRoot: Path = PROJECTROOT,
) -> tuple[str, ...]:
    """Return broken local hrefs and fragments from the exact rendered site."""

    siteRoot = siteRoot.resolve()
    referenceRoot = referenceRoot.resolve()
    htmlPaths = tuple(sorted(siteRoot.rglob("*.html")))

    if not htmlPaths:
        return (f"{_Relative(siteRoot, projectRoot)}: no rendered HTML files found",)

    pages = {}
    duplicateErrors = []

    for htmlPath in htmlPaths:
        parser = _PageParser()
        parser.feed(htmlPath.read_text(encoding="utf-8"))
        pages[htmlPath.resolve()] = parser

    errors = list(duplicateErrors)
    siteUrlPath = _SiteUrlPath(projectRoot)

    for htmlPath, parser in pages.items():
        sourcePath = _RenderedSourcePath(htmlPath, siteRoot, referenceRoot)
        sourceLabel = _Relative(sourcePath, projectRoot)

        for link in parser.links:
            parsedLink = urllib.parse.urlsplit(link)

            if parsedLink.scheme or link.startswith("//"):
                continue

            decodedPath = urllib.parse.unquote(parsedLink.path)

            if decodedPath.startswith("/"):
                if not decodedPath.startswith(siteUrlPath):
                    errors.append(
                        f"{sourceLabel}: absolute rendered link is outside site URL: {link}"
                    )
                    continue

                targetPath = (siteRoot / decodedPath[len(siteUrlPath) :]).resolve()

            else:
                targetPath = (htmlPath.parent / decodedPath).resolve()

            if not decodedPath:
                targetPath = htmlPath

            elif targetPath.is_dir() or targetPath.suffix == "":
                targetPath /= "index.html"

            try:
                targetPath.relative_to(siteRoot.resolve())

            except ValueError:
                errors.append(f"{sourceLabel}: rendered link escapes site: {link}")
                continue

            if not targetPath.is_file():
                errors.append(f"{sourceLabel}: missing rendered target: {link}")
                continue

            fragment = urllib.parse.unquote(parsedLink.fragment)

            if fragment and targetPath.suffix.lower() == ".html":
                targetParser = pages.get(targetPath)

                if targetParser is None:
                    targetParser = _PageParser()
                    targetParser.feed(targetPath.read_text(encoding="utf-8"))
                    pages[targetPath] = targetParser

                if fragment not in targetParser.anchors:
                    errors.append(
                        f"{sourceLabel}: missing rendered anchor {fragment!r}: {link}"
                    )

    return tuple(errors)


def ValidateGeneratedPolicy(projectRoot: Path = PROJECTROOT) -> tuple[str, ...]:
    """Return violations of ADR-0010's disposable generated-output policy."""

    trackedPaths = subprocess.check_output(
        ["git", "ls-files"], cwd=projectRoot, text=True
    ).splitlines()
    errors = []

    for trackedPath in trackedPaths:
        if trackedPath.startswith("_build/"):
            errors.append(f"{trackedPath}: generated _build output must not be committed")

        if trackedPath.startswith("docs/site/") and trackedPath.endswith(".html"):
            errors.append(f"{trackedPath}: generated reference HTML must not be committed")

    gitignoreText = (projectRoot / ".gitignore").read_text(encoding="utf-8")

    if "/_build/" not in gitignoreText.splitlines():
        errors.append(".gitignore: disposable /_build/ output is not ignored")

    return tuple(errors)


def ParseArguments(arguments=None):
    """Parse documentation-gate command arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "coverage",
            "locales",
            "source-links",
            "rendered-links",
            "generated-policy",
            "all",
        ),
    )
    parser.add_argument("--site-root", dest="siteRoot", type=Path, default=SITEROOT)
    return parser.parse_args(arguments)


def Main(arguments=None):
    """Run selected deterministic gates and print actionable violations."""

    options = ParseArguments(arguments)
    validators = {
        "coverage": lambda: ValidateCoverage(),
        "locales": lambda: ValidateLocales().diagnostics,
        "source-links": lambda: ValidateSourceLinks(),
        "rendered-links": lambda: ValidateRenderedLinks(options.siteRoot),
        "generated-policy": lambda: ValidateGeneratedPolicy(),
    }
    selectedNames = tuple(validators) if options.command == "all" else (options.command,)
    errors = []

    for selectedName in selectedNames:
        errors.extend(validators[selectedName]())

    if errors:
        for error in errors:
            print(error, file=sys.stderr)

        return 1

    print(f"Documentation {options.command} gate: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
