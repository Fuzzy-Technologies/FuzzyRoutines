<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines Development and Evidence Protocol

This protocol adapts the F-Tech engineering process to a foundational mathematical library.

It supplements the organization-wide GitHub workflow. The key distinction for this repository is that **mathematical correctness evidence and engineering/refactor evidence are not interchangeable**.

## 1. Change classes

Every PR should identify which evidence class applies.

### Mathematical behavior change

Examples:

- membership-function formulas;
- fuzzy negation;
- t-norm/s-norm behavior;
- defuzzification;
- fuzzy-set operations;
- numerical tolerance/edge-case semantics.

Required evidence:

- analytical reference values and/or established identities;
- invariant/property tests where applicable;
- boundary and degenerate-case tests;
- explicit tolerance policy;
- compatibility impact statement;
- ADR reference when semantics are being decided.

A green regression suite alone is not sufficient mathematical evidence.

### Compatibility change

Examples:

- public names;
- import paths;
- call signatures;
- parameter conventions;
- return shape;
- legacy aliases.

Required evidence:

- legacy API regression tests;
- real/historical consumer evidence;
- explicit classification as compatible correction vs intentional break;
- migration notes for intentional breaks.

A known mathematical bug is not a compatibility requirement.

### Refactor / architecture change

Examples:

- splitting the monolithic module;
- moving implementation into focused modules;
- introducing a facade;
- typing/internal cleanup.

Required evidence:

- no intended mathematical behavior change;
- legacy regression suite remains green;
- import/public API smoke remains green;
- focused new-module tests where applicable.

Do not mix broad refactoring with mathematical corrections unless the separation is impossible and explicitly justified.

### Packaging / CI / release change

Required evidence:

- exact build/test commands in CI logs;
- clean install/import smoke where applicable;
- no accidental publication during test PRs;
- explicit artifact/release evidence for publication work.

### Performance change

Required evidence:

- reproducible before/after benchmark;
- benchmark environment;
- representative workload;
- numerical parity within approved tolerance;
- memory/dependency impact when relevant.

No speculative optimization.

## 2. Evidence-first status

Do not report `PASS` unless the relevant command actually ran successfully.

Record failures honestly.

A placeholder command such as `ls -la` is not test evidence.

For critical changes, preserve enough information to reproduce:

- Git revision;
- Python version;
- command;
- dependency installation method;
- relevant numeric tolerance/configuration.

## 3. PR isolation

Prefer one coherent review concern per PR.

Keep these concerns separate when practical:

- baseline measurement;
- mathematical correction;
- compatibility adaptation;
- architecture extraction;
- packaging migration;
- performance optimization.

Independent Tasks may be implemented in parallel branches if they do not depend on each other and do not create avoidable file conflicts.

## 4. Test expectations

### Legacy regression tests

Protect historical names, imports, signatures, parameter conventions, and legitimate behavior.

Do not add a regression test whose sole purpose is to preserve a known mathematical defect.

### Mathematical tests

Prefer:

- exact reference values where analytically known;
- algebraic identities;
- range/monotonicity/symmetry properties;
- boundary tests;
- property-based tests when they materially improve confidence.

### Numerical tests

Every approximate assertion must have a reason for its tolerance.

Do not create one global epsilon for unrelated algorithms merely for convenience.

### Executable examples, tools, and benchmarks

Unit tests of internal builder functions do not prove that a user-facing entry
point works. Every new or changed executable example, CLI tool, benchmark, or
reporter must have at least one end-to-end invocation in a supported Python
environment. Verify its exit status and externally observable output.

For a tool that writes JSON to stdout, exercise the same shell boundary a user
will use: redirect stdout to a file and parse that file as JSON. When a tool
accepts an output path, exercise that path as well. Keep generated local reports
out of Git unless the task explicitly publishes versioned evidence.

### Python code style and quality standard

These rules apply to every Python file, including tests. They govern newly
written code and modified code paths; existing public names remain subject to
the compatibility policy.

#### Naming and compatibility

- Functions, methods, and classes use `PascalCase`, including `Main()`.
- Variables, parameters, and instance attributes use `lowerCamelCase`.
- Constants use unseparated `UPPERCASE` names, without underscores.
- Do not introduce `snake_case` in project-owned identifiers.
- Required Python dunder names, external API/SDK/protobuf/library names, and
  test-discovery names are exceptions. Test files retain the `test_*.py`
  convention; names after the mandatory `test_` prefix use `PascalCase`.
- Do not rename historical public identifiers, import paths, signatures, or
  parameter conventions merely to conform to this style. Such a change requires
  explicit compatibility classification and, where breaking, a migration plan.

#### Documentation and comments

- The canonical repository standard is
  [`docs/python-code-style.md`](python-code-style.md). It defines required
  module headers, Google-style sections, Markdown/API references, mathematical
  notation, and examples for production code, tests, and executable tools.
- Source code, docstrings, comments, tests, ADRs, and technical Issue/PR content
  are written in English.
- In Markdown, delimit inline mathematics with `$...$` and display mathematics
  with `$$...$$` so formulas render in JetBrains IDE and GitHub previews. Do not
  use `\(...\)` or `\[...\]` as Markdown math delimiters.
- Every production module, class, function, and method has a concise docstring
  that explains its responsibility and semantic contract. Python annotations
  remain authoritative for types; docstrings document domains, units,
  invariants, mathematical behavior, side effects, approximation status, and
  intentional exceptions without duplicating annotations.
- Module docstrings are the first Python statement, except that a shebang may
  precede the provenance header in a genuinely executable script. Every Python
  file carries the canonical FuzzyRoutines project, collective-maintainer,
  `SPDX-FileCopyrightText`, and `SPDX-License-Identifier` fields without a
  misleading single-person author claim. Generated-document constraints must
  not add import-time behavior or reduce source clarity.
- All project-owned source, tests, documentation, examples, tools, workflows,
  configuration, and site assets use `SPDX-License-Identifier: Apache-2.0` in
  the comment syntax appropriate to their format. `LICENSE`, `NOTICE`,
  [`docs/licensing.md`](licensing.md), and ADR-0012 define the authoritative
  licensing and provenance boundary. A contribution must not introduce an MIT
  or other license claim into a project-owned file.
- Before an implementation is handed off for review, its executor verifies
  every Acceptance Criterion against concrete evidence and checks the
  corresponding Issue checkbox. The reviewer reviews the PR; the reviewer is
  not responsible for maintaining the implementation Task checklist.
- FuzzyRoutines follows ADR-0010: canonical docstrings use English Google style
  with Markdown content and LaTeX mathematics. This repository-specific rule
  supersedes any older generic instruction requesting Russian production
  docstrings.
- Comments explain a reason, limitation, mathematical assumption, or
  architectural decision; they do not narrate obvious code.

#### Layout and formatting

- Separate logical blocks with intentional blank lines.
- Do not put a blank line immediately after the header of `def`, `class`,
  `try`, `if`, `elif`, `else`, `except`, `finally`, `for`,
  `while`, `with`, `match`, or `case`.
- Put one blank line before `elif`, `else`, `except`, and `finally`.
- Use two blank lines between module-level functions and one blank line between
  class methods. Put one blank line before `if __name__ == "__main__":`.
- Do not run `ruff format`: it removes intentional sparse formatting. Use
  `ruff check` where configured, and preserve this layout when applying any
  automated fix.
- Keep new Markdown tables readable without rendering: make cells concise and
  pad every source column to the width of its longest cell. Do not rewrite an
  otherwise unchanged historical table solely for alignment.

#### Implementation and validation

- The declared CPython support policy controls usable language features and
  dependencies. Type public APIs and non-trivial internal boundaries. Introduce
  dataclasses, protocols/ABCs, enums, explicit exceptions, or immutable value
  objects only when they clarify a contract; avoid speculative abstractions and
  framework-style complexity.
- Keep imports explicit, structured, and auditable. New production code must not
  use wildcard imports or obsolete Python idioms. Historical wildcard-import
  behavior is compatibility evidence, not a pattern for new code.
- Validate inputs at meaningful boundaries and fail with specific errors. Do not
  use broad exception handling or silently turn a failed calculation into zero,
  `None`, or another plausible result; preserve the original cause where
  appropriate.
- Assertion messages state the violated invariant and the likely reason for the
  failure. Use branch coverage. Critical resource-management, rollback, cleanup,
  and error-handling branches require tests.
- For mathematical changes, these rules supplement—not replace—the analytical,
  property, boundary, and tolerance evidence required above.

#### Infrastructure-like changes and gates

For a change to CI, Python IaC, cloud-init, TOML configuration profiles, network
rules, or hardening, first run and record the full relevant test baseline. After
the change, repeat the checks. Such changes require invariant and failure-path
tests without contacting a real external service.

Run focused checks first. The deterministic developer gate includes
formatting/linting, unit tests, property tests, and import/package smoke; the
full gate may add typing, branch coverage, build/clean-install,
benchmark-regression, and supported-CPython checks. After applicable
infrastructure-like changes, run tests, `ruff check`, `compileall`, and CLI
`--help` when the package exposes a CLI. No CI test may depend on an external
online service.

The canonical full-suite command is `python -m tools.test_runner`. It discovers
tests through pytest, runs parallel-safe scopes in pytest-xdist processes, and
runs tests marked `serial` in a separate sequential phase. The runner uses the
active `sys.executable`, so IDE and CI environments must install the same
`requirements.txt` test dependencies. Tests must use isolated temporary/state
roots and the shared database/port fixtures instead of repository-root files or
fixed ports. `--serial` and manual reruns are diagnostic tools; the gate never
retries a failing test automatically.

#### Git discipline

Commit messages are brief, imperative English sentences, for example
`Add analytical centroid tests`, `Fix Gaussian parameter validation`, or
`Update package installation gate`.

**Prefer explicitness over magic, evidence over assumption, tests over manual
checks, and stability over cosmetic refactoring.**

## 5. ADR gate

An ADR is required when changing a durable cross-cutting contract, including:

- compatibility policy;
- universe/support semantics;
- membership parameter conventions;
- operator/negation domain policy;
- defuzzification/numerical policy;
- packaging/versioning policy;
- mandatory runtime dependency/vectorization strategy.

An implementation PR must not silently decide an unresolved ADR.

## 6. Review handoff

Before asking for review:

- branch is based on `develop`;
- Task/Feature metadata is complete;
- PR has assignee, labels, and Milestone;
- linked Task is explicit in the PR body;
- CI is green or the failure is explicitly reported;
- Task comment records implementation/evidence/PR link;
- parent Feature receives a concise status comment when useful.

## 7. Merge and completion

Human review remains the default merge gate.

After merge:

- linked Task is closed as completed by repository automation;
- completion comment links the merged PR;
- merged branch is deleted when safe;
- Features are closed only after all required child Tasks and acceptance criteria are complete.

## 8. Security and secrets

Never commit:

- credentials;
- package-registry tokens;
- private keys;
- secrets copied from legacy CI.

Historical encrypted CI blobs must be treated as obsolete credential paths and retired through dedicated release-security work.

## 9. Canonical principle

**Mathematics requires proof-oriented evidence. Compatibility requires consumer/API evidence. Refactoring requires parity evidence. Performance requires measurement. Release claims require artifact evidence.**
