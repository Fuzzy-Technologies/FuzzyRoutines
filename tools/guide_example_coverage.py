# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Connect every inventoried public symbol to an actually executed guide example.

The locale validator owns static inventory freshness. This additional gate
profiles the exact published Python fences and observes constructor, method,
and property execution. Merely importing a symbol does not establish usage.
Typing contracts require an annotation; built-in exception constructors require
a retained concrete instance. No package source path is added to sys.path.
The default core report lists omitted optional pages and symbols. Select every
declared extra explicitly before generating or validating the complete index.
"""

import argparse
import ast
import contextlib
import importlib
import inspect
import io
import json
import runpy
import sys
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = PROJECT_ROOT / "docs/site/content/en"
INDEX_PATH = CONTENT_ROOT / "guides/example-index.md"
VERIFIER = runpy.run_path(str(PROJECT_ROOT / "tools/verify_installed_executables.py"))
TYPE_CONTRACT_NAMES = frozenset({
    "fuzzyroutines.MembershipCallable", "fuzzyroutines.MembershipScalar",
    "fuzzyroutines.membership.MembershipCallable", "fuzzyroutines.membership.MembershipScalar",
    "fuzzyroutines.inference.Antecedent",
})


def PublicTargets():
    """Resolve hash-bound public inventory and verify canonical root alias identity."""

    units = tomllib.loads((PROJECT_ROOT / "docs/i18n/units.toml").read_text())
    manifest = tomllib.loads((PROJECT_ROOT / "docs/site/api-coverage.toml").read_text())
    modules = sorted((surface["module"] for surface in manifest["surfaces"]), key=len, reverse=True)
    targets = {}

    for unit in units["units"]:
        if unit["kind"] != "symbol":
            continue

        name = unit["id"].removeprefix("symbol:")
        moduleName = next(module for module in modules if name.startswith(module + "."))
        target = importlib.import_module(moduleName)

        for part in name.removeprefix(moduleName + ".").split("."):
            target = getattr(target, part)

        targets[name] = target

    package = importlib.import_module("fuzzyroutines")
    syntax = ast.parse((PROJECT_ROOT / "fuzzyroutines/__init__.py").read_text())

    for node in syntax.body:
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue

        for alias in node.names:
            name = alias.asname or alias.name

            if name not in package.__all__:
                continue

            canonical = getattr(importlib.import_module(node.module), alias.name)

            if targets.get(f"fuzzyroutines.{name}") is not canonical:
                raise RuntimeError(f"missing or changed canonical root alias: {name}")

    return targets


def TargetCodes(targets):
    """Associate unwrapped Python code identities with all corresponding public names."""

    codes = {}
    builtinClasses = {}

    for name, target in targets.items():
        if name in TYPE_CONTRACT_NAMES:
            continue

        callableTarget = target.fget if isinstance(target, property) else target

        if inspect.isclass(callableTarget):
            callableTarget = callableTarget.__init__

        code = getattr(inspect.unwrap(callableTarget), "__code__", None)

        if code is not None:
            codes.setdefault(id(code), set()).add(name)

        elif inspect.isclass(target) and issubclass(target, Exception):
            builtinClasses.setdefault(target, set()).add(name)

        else:
            raise RuntimeError(f"public symbol needs an explicit usage contract: {name}")

    return codes, builtinClasses


def ObservedValues(namespace):
    """Walk retained example values without inspecting imported modules or classes."""

    pending = [value for name, value in namespace.items() if not name.startswith("__")]
    seen = set()

    while pending:
        value = pending.pop()

        if id(value) in seen:
            continue

        seen.add(id(value))
        yield value

        if isinstance(value, dict):
            pending.extend(value.values())

        elif isinstance(value, (tuple, list)):
            pending.extend(value)


def ExecuteExamples(examples, targets):
    """Run standalone snippets and retain observed public execution per snippet."""

    codes, builtinClasses = TargetCodes(targets)
    coverage = {name: [] for name in targets}

    for exampleName, snippet in examples.items():
        observed = set()
        namespace = {"__name__": "__guide_example__"}

        def Profile(frame, event, argument, observed=observed):
            """Record only actual calls to inventoried project code objects."""

            if event == "call":
                observed.update(codes.get(id(frame.f_code), ()))

        previousProfile = sys.getprofile()

        try:
            with contextlib.redirect_stdout(io.StringIO()):
                sys.setprofile(Profile)
                # Execute trusted repository guide code; imports alone cannot prove usage.
                exec(compile(snippet, exampleName, "exec"), namespace)  # noqa: S102

        finally:
            sys.setprofile(previousProfile)

        annotations = list(namespace.get("__annotations__", {}).values())

        if "__annotate__" in namespace:
            import annotationlib

            annotations.extend(annotationlib.call_annotate_function(namespace["__annotate__"], annotationlib.Format.VALUE).values())

        for value in ObservedValues(namespace):
            observed.update(builtinClasses.get(type(value), ()))

            if inspect.isfunction(value):
                annotations.extend(value.__annotations__.values())

        for name in TYPE_CONTRACT_NAMES & targets.keys():
            if any(annotation is targets[name] for annotation in annotations):
                observed.add(name)

        for name in sorted(observed):
            coverage[name].append(exampleName)

    return coverage


def BuildReport(examples=None, targets=None, extras=()):
    """Return execution evidence for the selected scope and explicit omissions."""

    optionalScopes = VERIFIER["OptionalExampleScopes"]()
    unknownExtras = set(extras) - optionalScopes.keys()

    if unknownExtras:
        raise ValueError(f"Unknown guide extras: {sorted(unknownExtras)}")

    omittedModules = tuple(
        module for extra, scope in optionalScopes.items() if extra not in extras
        for module in scope["modules"]
    )
    omittedPages = sorted(
        page for extra, scope in optionalScopes.items() if extra not in extras
        for page in scope["pages"]
    )
    examples = VERIFIER["LoadCanonicalGuideExamples"](extras=extras) if examples is None else examples
    targets = PublicTargets() if targets is None else targets
    omittedSymbols = sorted(
        name for name in targets if any(name == module or name.startswith(module + ".") for module in omittedModules)
    )
    targets = {name: target for name, target in targets.items() if name not in omittedSymbols}
    coverage = ExecuteExamples(examples, targets)
    package = importlib.import_module("fuzzyroutines")

    return {
        "schemaVersion": 2,
        "extras": sorted(set(extras)),
        "omittedOptionalPages": omittedPages,
        "omittedOptionalSymbols": omittedSymbols,
        "packageOrigin": str(Path(package.__file__).resolve()),
        "exampleCount": len(examples),
        "symbolCount": len(coverage),
        "coverage": coverage,
        "missing": [name for name, exampleNames in coverage.items() if not exampleNames],
    }


def RenderIndex(report):
    """Produce a deterministic reader-facing symbol-to-example table."""

    if report["missing"]:
        raise RuntimeError("cannot render an incomplete public example index")

    if report.get("omittedOptionalPages") or report.get("omittedOptionalSymbols"):
        raise RuntimeError("canonical index requires every declared optional extra")

    pages = {}

    for path in sorted(CONTENT_ROOT.rglob("*.md")):
        relativePath = path.relative_to(CONTENT_ROOT).with_suffix("")
        key = "canonical-" + "-".join(relativePath.parts)
        pages[key] = path.relative_to(INDEX_PATH.parent).as_posix() if path.is_relative_to(INDEX_PATH.parent) else "../" + path.relative_to(CONTENT_ROOT).as_posix()

    rows = [("Public symbol", "Executable examples")]
    optionalPrefixes = tuple(
        "canonical-" + "-".join(Path(page).with_suffix("").parts) + "-"
        for scope in VERIFIER["OptionalExampleScopes"]().values() for page in scope["pages"]
    )

    for name, examples in sorted(report["coverage"].items()):
        links = []

        # Prefer dependency-free evidence for symbols shared by core and extras.
        orderedExamples = sorted(examples, key=lambda name: (name.startswith(optionalPrefixes), name))

        for exampleName in orderedExamples[:2]:
            pageKey, _, number = exampleName.rpartition("-")
            path = pages[pageKey]
            links.append(f"[{Path(path).stem}, block {number}]({path})")

        rows.append((f"`{name}`", "; ".join(links)))

    widths = [max(len(row[column]) for row in rows) for column in range(2)]
    rows.insert(1, tuple("-" * width for width in widths))
    table = "\n".join("| " + " | ".join(cell.ljust(width) for cell, width in zip(row, widths, strict=True)) + " |" for row in rows)
    header = (
        "<!--\nSPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies\n"
        "SPDX-License-Identifier: Apache-2.0\n-->\n\n# Public API example index\n\n"
        f"All {report['symbolCount']} inventoried public symbols are linked to executed "
        f"examples ({report['exampleCount']} standalone Python blocks), with every "
        "declared optional extra enabled. Root exports "
        "are verified aliases of the corresponding module objects.\n\n"
        "Functions, constructors, methods and properties require actual execution; "
        "imports alone do not count. Result constructors also run when their producer "
        "returns them; see [result records](results.md) for explicit reconstruction. "
        "Typing contracts require a real annotation, and exception classes "
        "require constructed instances. Private helpers and generated dataclass "
        "methods remain outside the authored public inventory.\n\n"
        "This index establishes example availability, not independent proof of every "
        "mathematical branch. Review the linked explanations, limits and assertions. "
        "CI regenerates the evidence against an installed package and rejects stale "
        "index content. At most two examples per symbol are shown.\n\n"
    )

    return header + table + "\n"


def ValidateIndex(report, indexText):
    """Check full index content or only observed core rows with explicit omissions."""

    if not report["omittedOptionalPages"] and not report["omittedOptionalSymbols"]:
        if indexText != RenderIndex(report):
            raise RuntimeError("stale public API example index; run --write-index with all extras")

        return

    scopedReport = dict(report, omittedOptionalPages=[], omittedOptionalSymbols=[])
    expectedRows = {
        row.split("|")[1].strip(): tuple(cell.strip() for cell in row.split("|")[1:-1])
        for row in RenderIndex(scopedReport).splitlines() if row.startswith("| `")
    }
    actualRows = {}

    for row in indexText.splitlines():
        if not row.startswith("| `"):
            continue

        cells = tuple(cell.strip() for cell in row.split("|")[1:-1])

        if cells[0] in actualRows:
            raise RuntimeError(f"duplicate public API example index row: {cells[0]}")

        actualRows[cells[0]] = cells

    optionalDestinations = {
        Path(page).relative_to("guides").as_posix() if page.startswith("guides/") else "../" + page
        for page in report["omittedOptionalPages"]
    }

    for name, expectedRow in expectedRows.items():
        actualRow = actualRows.get(name)

        if actualRow is None or len(actualRow) != 2:
            raise RuntimeError(f"missing or malformed core index row: {name}")

        expectedLinks = expectedRow[1].split("; ")
        actualLinks = actualRow[1].split("; ")
        optionalLinks = actualLinks[len(expectedLinks):]

        if (
            len(actualLinks) > 2 or actualLinks[:len(expectedLinks)] != expectedLinks
            or any(not any(link.endswith(f"]({path})") for path in optionalDestinations) for link in optionalLinks)
        ):
            raise RuntimeError(f"stale core row in public API example index: {name}")


def Main(arguments=None):
    """Validate execution coverage and optionally write explicit evidence or index."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-installed", action="store_true", dest="requireInstalled")
    parser.add_argument("--extra", action="append", default=[], choices=tuple(VERIFIER["OptionalExampleScopes"]()))
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write-index", action="store_true", dest="writeIndex")
    modes.add_argument("--check-index", action="store_true", dest="checkIndex")
    options = parser.parse_args(arguments)
    report = BuildReport(extras=options.extra)

    if options.requireInstalled and not Path(report["packageOrigin"]).is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError(f"package resolved outside installed environment: {report['packageOrigin']}")

    if options.output is not None:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    if not report["missing"]:
        if options.writeIndex:
            INDEX_PATH.write_text(RenderIndex(report))

        elif options.checkIndex:
            ValidateIndex(report, INDEX_PATH.read_text())

    print(json.dumps({key: report[key] for key in (
        "symbolCount", "exampleCount", "missing", "extras", "omittedOptionalPages", "omittedOptionalSymbols",
    )}, sort_keys=True))

    return 1 if report["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(Main())
