# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Repository-wide naming contracts, including embedded executable Python."""

import ast
import re
import subprocess
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CAMEL_CASE = re.compile(r"_?[a-z][A-Za-z0-9]*\Z")
PASCAL_CASE = re.compile(r"_?[A-Z][A-Za-z0-9]*\Z")
CONSTANT_CASE = re.compile(r"_?[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*\Z")
TEST_CASE = re.compile(r"test_[A-Z][A-Za-z0-9]*\Z")
SPHINX_SETTINGS = frozenset({
    "html_theme", "html_theme_options", "autodoc_typehints",
    "napoleon_google_docstring", "napoleon_numpy_docstring",
})
# These are upstream override points, never a blanket snake_case allowance.
EXTERNAL_METHODS = {
    "tools/locale_griffe_extension.py": {"on_instance"},
    "tools/locale_site_hook.py": {"on_page_context", "on_page_markdown"},
    "tools/reproducible_artifacts.py": {"make_archive"},
    "tools/documentation_gates.py": {"handle_starttag"},
    "tests/test_pages_site.py": {"handle_starttag"},
}
SETUPTOOLS_PARAMETERS = frozenset({"base_name", "root_dir", "base_dir"})
# AST/discovery tests contain importlib hook implementations as embedded source.
IMPORTLIB_HOOK_HOSTS = frozenset({
    "tests/test_curated_exports.py", "tests/test_focused_modern_modules.py",
    "tests/test_vectorized_optional_boundary.py", "tests/test_legacy_facade.py",
    "tools/build_api_reference.py",
})


def _Dunder(name):
    """Recognize Python-reserved magic bindings without admitting private snake_case."""

    return name.startswith("__") and name.endswith("__")


def _Property(node):
    """Identify field accessors whose method names must equal their camelCase fields."""

    return any(
        isinstance(decorator, ast.Name) and decorator.id == "property"
        or isinstance(decorator, ast.Attribute) and decorator.attr in {"setter", "deleter"}
        for decorator in node.decorator_list
    )


def _NamingViolations(sourceText, relativePath, *, embedded=False):
    """Report project declarations while preserving explicitly owned external boundaries."""

    tree = ast.parse(sourceText)
    violations = []
    externalParameters = set()
    externalReferences = set()
    typeAliasNames = {id(node.name) for node in ast.walk(tree) if isinstance(node, ast.TypeAlias)}
    invalidFixtures = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "make_archive":
            if relativePath == "tools/reproducible_artifacts.py":
                externalParameters.update(id(argument) for argument in node.args.args)
                externalReferences.update(id(child) for child in ast.walk(node) if isinstance(child, ast.Name))

        if relativePath == "tests/test_python_naming.py" and isinstance(node, ast.FunctionDef):
            if node.name in {"test_NamingGuardRejectsSnakeCaseAndChecksEmbeddedPython", "test_ExternalExceptionCannotHideOrdinarySnakeCaseLocals"}:
                invalidFixtures.update(id(child) for child in ast.walk(node) if isinstance(child, ast.Constant))

    for node in ast.walk(tree):
        name = None
        valid = True

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            valid = bool(PASCAL_CASE.fullmatch(name)) or _Dunder(name)

            if name.startswith("test_"):
                valid = bool(TEST_CASE.fullmatch(name))

            elif _Property(node):
                valid = bool(CAMEL_CASE.fullmatch(name))

            elif name in EXTERNAL_METHODS.get(relativePath, set()):
                valid = True

            elif embedded and relativePath in IMPORTLIB_HOOK_HOSTS and name == "find_spec":
                valid = True

            elif relativePath == "fuzzyroutines/membership.py" and name == "mju":
                # Analytical adapters preserve the historical evaluator protocol.
                valid = True

        elif isinstance(node, ast.ClassDef):
            name = node.name
            valid = bool(PASCAL_CASE.fullmatch(name))

        elif isinstance(node, ast.arg):
            name = node.arg
            valid = bool(CAMEL_CASE.fullmatch(name)) or name == "_"

            if id(node) in externalParameters and name in SETUPTOOLS_PARAMETERS:
                valid = True

        elif isinstance(node, ast.Name):
            name = node.id
            valid = bool(CAMEL_CASE.fullmatch(name) or CONSTANT_CASE.fullmatch(name)) or name == "_" or _Dunder(name)

            if isinstance(node.ctx, ast.Load):
                valid = valid or bool(PASCAL_CASE.fullmatch(name) or TEST_CASE.fullmatch(name))

                if id(node) in externalReferences and name in SETUPTOOLS_PARAMETERS:
                    valid = True

            if relativePath == "docs/api-evaluation/sphinx/conf.py" and name in SPHINX_SETTINGS:
                valid = True

            elif id(node) in typeAliasNames:
                valid = bool(PASCAL_CASE.fullmatch(name))

        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            name = node.attr
            valid = bool(CAMEL_CASE.fullmatch(name)) or _Dunder(name)

            if relativePath == "tests/test_reproducible_artifacts.py" and name == "dry_run":
                valid = True

            elif relativePath == "tools/reproducible_artifacts.py" and name == "pax_headers":
                valid = True

        elif isinstance(node, ast.alias):
            name = node.asname or node.name.split(".")[0]
            valid = bool(CAMEL_CASE.fullmatch(name) or PASCAL_CASE.fullmatch(name) or CONSTANT_CASE.fullmatch(name))

            if name == "*":
                # Historical wildcard consumers are compatibility evidence.
                valid = True

        elif isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)) and node.name:
            name = node.name
            valid = bool(CAMEL_CASE.fullmatch(name)) or name == "_"

        if name and not valid:
            violations.append(f"{relativePath}:{node.lineno}: {name}")

        if not embedded and isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in invalidFixtures:
                continue

            if not re.search(r"(?m)^\s*(?:from |import |(?:async )?def |class )", node.value):
                continue

            try:
                nested = _NamingViolations(node.value, relativePath, embedded=True)

            except SyntaxError:
                # Intentionally incomplete/invalid parser fixtures are data.
                continue

            violations.extend(f"{violation} (embedded at line {node.lineno})" for violation in nested)

    return violations


def test_NamingGuardRejectsSnakeCaseAndChecksEmbeddedPython():
    """Reject local/parameter/field names and discover declarations in executable fixtures."""

    sourceText = 'def Calculate(input_value):\n    local_value = input_value\n    return local_value\n'
    violations = _NamingViolations(sourceText, "example.py")

    assert any("input_value" in violation for violation in violations)
    assert any("local_value" in violation for violation in violations)
    assert _NamingViolations("program = 'def Calculate(input_value): pass'", "example.py")
    assert not _NamingViolations("def Calculate(inputValue):\n    return inputValue\n", "example.py")


def test_ExternalExceptionCannotHideOrdinarySnakeCaseLocals():
    """Limit a setuptools exemption to its imposed override signature."""

    sourceText = 'def make_archive(self, base_name, root_dir=None):\n    archive_path = base_name\n'
    violations = _NamingViolations(sourceText, "tools/reproducible_artifacts.py")

    assert len(violations) == 1 and "archive_path" in violations[0]
    assert {violation.rsplit(": ", 1)[-1] for violation in _NamingViolations(sourceText, "example.py")} == {
        "make_archive", "base_name", "root_dir", "archive_path",
    }


def test_AllTrackedPythonDeclarationsFollowProjectNaming():
    """Audit every Python file, including tooling, fixtures, experiments and configuration."""

    output = subprocess.check_output(["git", "ls-files", "-z", "*.py"], cwd=PROJECT_ROOT, text=True)
    violations = []

    for relativePath in output.split("\0"):
        if relativePath:
            violations.extend(_NamingViolations((PROJECT_ROOT / relativePath).read_text(encoding="utf-8"), relativePath))

    assert not violations, "Python naming violations:\n" + "\n".join(violations)


def test_AuthoredMarkdownPythonExamplesFollowProjectNaming():
    """Check executable Python fences alongside their standalone source counterparts."""

    output = subprocess.check_output(["git", "ls-files", "-z", "*.md"], cwd=PROJECT_ROOT, text=True)
    violations = []

    for relativePath in output.split("\0"):
        if not relativePath:
            continue

        sourceText = (PROJECT_ROOT / relativePath).read_text(encoding="utf-8")

        for match in re.finditer(r"(?m)^(`{3,}|~{3,})python[^\n]*\n(.*?)^\1\s*$", sourceText, re.DOTALL):
            try:
                violations.extend(_NamingViolations(match[2], relativePath))

            except SyntaxError:
                # A signature fragment does not represent an executable program.
                continue

    assert not violations, "Markdown Python naming violations:\n" + "\n".join(violations)


def test_AuthoredWorkflowPythonFollowsProjectNaming():
    """Cover inline Python heredocs without treating shell/YAML schema names as identifiers."""

    output = subprocess.check_output(["git", "ls-files", "-z", "*.yml", "*.yaml"], cwd=PROJECT_ROOT, text=True)
    violations = []
    pattern = re.compile(r"<<[ \t]*['\"](?P<marker>PY[A-Z_]*)['\"][^\n]*\n(?P<program>.*?)(?m:^[ \t]*(?P=marker)[ \t]*$)", re.DOTALL)

    for relativePath in output.split("\0"):
        if not relativePath:
            continue

        sourceText = (PROJECT_ROOT / relativePath).read_text(encoding="utf-8")

        for match in pattern.finditer(sourceText):
            violations.extend(_NamingViolations(textwrap.dedent(match["program"]), relativePath))

    assert not violations, "Workflow Python naming violations:\n" + "\n".join(violations)
