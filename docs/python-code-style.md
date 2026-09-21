<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Python Code and Source Documentation Standard

This document is the canonical Python source-style contract for
FuzzyRoutines. It applies to production modules, tests, examples, benchmarks,
and executable tools. Historical public names remain governed by
[ADR-0001](adr/0001-backward-compatibility-contract.md); this standard does not
authorize compatibility-breaking renames.

[ADR-0010](adr/0010-api-documentation-architecture.md) is authoritative for
source documentation. FuzzyRoutines therefore uses **English Google-style
docstrings with Markdown content and LaTeX mathematics**. Any generic or older
F-Tech rule that requests Russian production docstrings is overridden for this
repository.

## Naming and compatibility

- Functions, methods, and classes use `PascalCase`, including `Main()`.
- Variables, parameters, and instance attributes use `lowerCamelCase`.
- Constants use unseparated `UPPERCASE` names without underscores.
- Project-owned identifiers do not introduce `snake_case`.
- Python dunder names, external API names, and test discovery are exceptions.
  Test files keep `test_*.py`; names after the mandatory `test_` prefix use
  `PascalCase`.
- Historical public identifiers, import paths, signatures, and parameter
  conventions are not renamed solely for style compliance.

## Canonical source-documentation contract

Python annotations declare types. Docstrings declare meaning. A docstring must
explain the semantic information a reader cannot reliably infer from a
signature alone: mathematical behavior, units, coordinate systems, valid
domains, boundary conventions, invariants, mutation or ownership rules,
side effects, approximation status, and intentional failures.

| Source object      | Requirement | Required contract                                                                                    |
|--------------------|-------------|------------------------------------------------------------------------------------------------------|
| Production module  | Required    | Ownership and license header, responsibility, semantic boundary, and import-time constraints         |
| Production class   | Required    | Represented concept, invariants, mutability or ownership, and attributes whose meaning is nontrivial |
| Function or method | Required    | Operation, mathematical semantics, argument domains, result meaning, and intentional exceptions      |
| Test module        | Required    | Contract or evidence family covered by the module                                                    |
| Individual test    | Optional    | Add only when the discovery name and assertions do not explain the invariant sufficiently            |
| Example module     | Required    | User scenario and whether it demonstrates compatibility or the modern API                            |
| Executable tool    | Required    | User-visible purpose, inputs and outputs, side effects, and failure boundary                         |

The first line is a concise summary ending with a period. Use an imperative
verb for a function or method (`Return`, `Evaluate`, `Validate`) and a noun
phrase for a class or module (`Immutable ...`, `Utilities for ...`). Add a
body only when it carries contract information. Do not repeat the Python name,
signature, annotation, or obvious implementation steps in prose.

Every production module, class, function, and method receives a docstring,
including non-public helpers when they encode a mathematical or architectural
boundary. A property docstring states the value's meaning, not that it “gets”
the value. Constructors may rely on the class docstring when `__init__` adds no
independent contract; an explicit `__init__` with additional validation or
side effects documents that behavior.

### Google-style sections

Use only the sections needed by the contract and keep them in this order:

| Section       | Use when                                                                                       |
|---------------|------------------------------------------------------------------------------------------------|
| `Args:`       | A callable accepts arguments; document meaning, domain, units, ownership, or default semantics |
| `Returns:`    | A callable returns a value whose semantic meaning is not fully obvious                         |
| `Yields:`     | A generator yields values; do not use `Returns:` for yielded items                             |
| `Raises:`     | The implementation deliberately rejects a public condition                                     |
| `Attributes:` | Public class attributes need semantic explanation beyond their annotations                     |
| `Examples:`   | A short executable use case materially clarifies the contract                                  |
| `Notes:`      | Mathematical, numerical, compatibility, or provenance constraints need focused explanation     |

Do not put types in `Args:`, `Returns:`, `Yields:`, or `Attributes:` when
annotations already declare them. Document every public argument, but omit a
section that would contain only redundant text such as “The input value.”
Private helpers may use a summary-only docstring when their full domain is
already enforced and documented by the public boundary.

`Raises:` lists exceptions intentionally raised as part of the callable's
contract. It does not speculate about every incidental exception Python or a
dependency could raise. Error documentation must match fail-closed behavior;
never document clamping, coercion, or fallback behavior that does not exist.

### Markdown, references, and mathematics

- Use ordinary Markdown, not reStructuredText roles or Sphinx directives.
- Link API objects with qualified mkdocstrings references, for example
  `[ScalarFuzzySet][fuzzyroutines.fuzzysets.ScalarFuzzySet]`.
- Use backticks for identifiers, literal values, and short expressions.
- Use `$...$` for inline LaTeX and `$$...$$` for a display block when a formula
  is clearer than prose. Do not use `\\(...\\)` or `\\[...\\]` as Markdown
  delimiters: the canonical MkDocs pipeline and JetBrains Markdown preview use
  the dollar-delimited form. Define every symbol that is not already part of
  the callable's documented arguments.
- Use an `r` prefix for a docstring containing LaTeX backslashes, or escape
  each backslash explicitly. Raw docstrings are preferred when their final
  character is not a backslash.
- Use fenced `python` examples that are deterministic, minimal, and consistent
  with the supported API. Do not include prompts or generated output unless
  the output itself is the contract.
- State whether numerical output is exact, analytical, sampled, estimated, or
  tolerance-dependent. A sampled result must never be described as proof of a
  continuous property.

## Module-header standard

Every project-owned Python file identifies the project, collective maintainer,
copyright provenance, and effective license in a compact comment header. New
files use this exact order:

```python
# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0
```

Replace `2026` with the first year of project-owned copyrightable content in
that file. Use a range such as `2019-2026` only when Git history demonstrates
project-owned copyrightable changes in both the first and last year; do not
advance a year merely because time passed. Existing files retain documented
historical provenance during the repository-wide migration.

`Fuzzy Technologies contributors` is the canonical maintainer value. Do not
add a single-person `Author:` line to an ordinary project file: it becomes
stale and falsely attributes later work to the original author. Individual
authorship and contributions are established by Git history, for example
`git log --follow -- path/to/file.py`. A release or security contact belongs
in repository metadata or a dedicated ownership file, not in an authorship
claim inside every module.

Copied or derived third-party code keeps every evidenced copyright holder in
separate `SPDX-FileCopyrightText` lines and records its source in an adjacent
`# Source:` line. Its actual SPDX license identifier replaces `Apache-2.0`
when required by the reviewed upstream license; such material must also be
listed in `NOTICE` or a dedicated third-party notice manifest. Never relabel
external code as solely owned by Fuzzy Technologies.

The module docstring is the first Python statement after the comment header.
A shebang may precede the header only for a genuinely directly executable
script. A `from __future__` import, standard-library imports, third-party
imports, and local imports follow the docstring in that order, separated into
groups when more than one group is present.

Do not add filename banners, repeated package names, change logs, decorative
separators, or redundant person lists. The SPDX and project-maintainer fields
are the complete ordinary file header.

A production module header uses this shape:

```python
# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Exact alpha-cut operations for scalar fuzzy sets.

Discrete universes are evaluated exhaustively. Continuous callables require an
explicit sampled operation because finite inspection cannot prove their exact
geometry.
"""

from dataclasses import dataclass

from fuzzyroutines.domain import DiscreteUniverse
```

Importing a library module must not run examples, parse command-line
arguments, write files, access the network, or perform expensive evaluation.
If a necessary import-time action exists, document and test it explicitly.

## Examples by source kind

The examples below define documentation shape; they do not introduce new
library APIs.

### Mathematical function

```python
def WeakAlphaCut(fuzzySet: ScalarFuzzySet, alpha: Real) -> DiscreteRegion:
    r"""Return the weak alpha-cut of a discrete fuzzy set.

    The cut uses the inclusive boundary
    $A_\alpha = \{x \in X \mid \mu_A(x) \geq \alpha\}$.

    Args:
        fuzzySet: Set over an exhaustively enumerable discrete universe.
        alpha: Membership threshold in the closed interval $[0, 1]$.

    Returns:
        Coordinates whose validated membership grades are at least `alpha`.

    Raises:
        TypeError: The set does not use a discrete universe.
        ValueError: `alpha` is outside $[0, 1]$.

    Notes:
        `alpha=0` returns the declared universe and `alpha=1` returns the core.
    """
```

The annotations carry Python types; the formula and prose define the inclusive
boundary and both endpoint semantics.

### Class

```python
@dataclass(frozen=True, slots=True)
class IntegrationDomain:
    """Finite closed interval used by a continuous numerical operation.

    The domain is an operational bound, not the mathematical support of a
    fuzzy set.

    Attributes:
        left: Finite included lower endpoint.
        right: Finite included upper endpoint greater than `left`.
    """

    left: Real
    right: Real
```

The class documentation distinguishes the represented concept from a nearby
but mathematically different concept and states its invariant.

### Module

```python
# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Immutable linguistic terms and ordered linguistic scales.

This module defines representation only. It deliberately does not select a
lookup, tie-breaking, or fuzzification policy.
"""
```

The second paragraph records a negative architectural boundary that users
could not infer from the filename.

### Test

```python
# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Executable contracts for exact and sampled weak alpha-cuts."""


def test_HigherAlphaCutIsNestedInsideLowerCut():
    lowerCut = AlphaCut(fuzzySet, 0.25)
    higherCut = AlphaCut(fuzzySet, 0.75)

    assert set(higherCut.points) <= set(lowerCut.points), (
        "For beta >= alpha, A_beta must remain a subset of A_alpha."
    )
```

The test name and assertion message already state the invariant, so an
individual test docstring would add no useful information.

### Executable tool

```python
#!/usr/bin/env python3
# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Emit a reproducible membership benchmark report as JSON.

The command writes only the report to stdout and sends diagnostics to stderr.
It does not modify repository files or contact external services.
"""


def Main(arguments: Sequence[str] | None = None) -> int:
    """Run the benchmark command and return its process exit code.

    Args:
        arguments: Optional command-line arguments without the executable name.
            `None` reads the active process arguments.

    Returns:
        Zero after emitting a complete JSON report.

    Raises:
        ValueError: A requested workload size is not positive.
    """


if __name__ == "__main__":
    raise SystemExit(Main())
```

Tool documentation separates machine-readable stdout from diagnostics and
states side-effect and network boundaries. End-to-end tests must exercise the
same shell-visible entry point.

## Comments and generated documentation

Comments explain why a constraint, formula branch, compatibility adapter, or
failure path exists. They do not narrate control flow. English is mandatory in
production code, tests, examples, and tools.

Generated API documentation must not reduce source clarity:

- do not add empty sections, repeated annotations, renderer-specific filler,
  or import-time behavior merely to improve generated pages;
- do not commit generated HTML, inventories, search indexes, or source views;
- keep qualified references resolvable under strict mkdocstrings builds;
- prefer a clear source docstring over markup that only looks correct in one
  renderer;
- keep documentation-only dependencies outside runtime package metadata.

## Layout and validation

- A docstring is the first statement in its scope. Leave one blank line after
  a multi-line docstring before implementation.
- Leave two blank lines between module-level definitions and one blank line
  between class methods.
- Leave one blank line before `elif`, `else`, `except`, and `finally`, and
  before `if __name__ == "__main__":`.
- Do not run `ruff format`; use `ruff check` and preserve intentional sparse
  layout.
- Keep Markdown tables readable in source by padding each column to its widest
  cell. Do not realign an otherwise untouched historical table solely for
  appearance.
- Validate changed links, fenced examples, table structure, `ruff check`,
  `compileall`, and focused tests before review. Documentation generators are
  additional evidence; they do not replace source and behavioral checks.
