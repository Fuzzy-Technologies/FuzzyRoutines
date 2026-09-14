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
