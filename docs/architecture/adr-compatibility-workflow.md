# ADR and Compatibility Change Workflow

This document defines when FuzzyRoutines requires an Architecture Decision Record and how compatibility-affecting changes are reviewed.

It implements the repository compatibility principle:

> Historical public names and import paths are preserved. Mathematical, logical, numerical and theoretical defects are corrected under those names where possible. A known mathematical bug is not a compatibility requirement.

## 1. When an ADR is required

Create or resolve an ADR before implementation when a change defines or changes a durable cross-cutting contract.

ADR-required examples:

- backward-compatibility policy;
- universe / integration-domain / mathematical-support semantics;
- membership-function parameter conventions;
- fuzzy operator family or negation-domain policy;
- numerical tolerance or defuzzification policy;
- packaging/versioning/release policy;
- mandatory dependency or vectorization strategy.

An ADR is not required for a local implementation detail that follows an already approved contract.

## 2. Compatibility classification

Every public-behavior change must be classified before merge.

### Compatible implementation change

No documented/public contract changes.

Examples:

- internal refactor;
- extraction into focused modules behind the same facade;
- performance improvement with equivalent results;
- test/documentation improvements.

Required evidence:

- existing compatibility tests remain green;
- no intentional public signature/import/parameter change.

### Compatible defect correction

Historical callable names remain, but an invalid result or failure mode is corrected.

Examples:

- rejecting a mathematically invalid parameter value;
- replacing a non-terminating numerical search;
- correcting stale derived state;
- correcting a formula/logic defect.

Required evidence:

- the defect is explicitly documented;
- the corrected behavior has mathematical/reference tests;
- regression tests do not preserve the known defect;
- downstream impact is reviewed.

A known mathematical defect is **not** protected merely because old code produced it.

### Intentional breaking change

A protected name, import path, signature, parameter convention, or return contract is removed or incompatibly changed.

Required before implementation:

1. explicit ADR or approved compatibility decision;
2. concrete reason that compatibility cannot reasonably be preserved;
3. consumer-impact review;
4. migration path/documentation;
5. versioning decision consistent with the packaging/versioning ADR;
6. explicit human approval.

Naming cleanup by itself is not sufficient justification for a breaking change.

## 3. Protected surface

The protected surface is evidence-driven.

Primary evidence sources:

- legacy public API snapshot;
- README/documented examples;
- current internal Fuzzy Technologies consumers;
- known historical consumers;
- compatibility regression tests.

Unknown external use remains unknown. Do not infer that an undocumented consumer does not exist.

## 4. Decision flow

Use this decision sequence for a proposed change:

```text
Does it affect public behavior/name/import/signature/parameter convention?
    |
    +-- no --> normal implementation/review
    |
    +-- yes
         |
         +-- Is current behavior a documented mathematical/logical/numerical defect?
         |      |
         |      +-- yes --> compatible defect correction when names/contracts can remain
         |      |           + mathematical evidence
         |      |           + impact review
         |      |
         |      +-- no --> can compatibility be preserved with facade/alias/adapter?
         |                  |
         |                  +-- yes --> preserve compatibility
         |                  |
         |                  +-- no --> intentional breaking change
         |                              + ADR
         |                              + migration plan
         |                              + human approval
         |
         +-- unresolved semantic contract --> ADR before implementation
```

## 5. Human approval gate

Intentional breaking changes require explicit human approval before merge.

CI success cannot substitute for this approval.

The PR must link:

- the ADR/decision;
- affected compatibility tests;
- consumer-impact evidence;
- migration notes when applicable.

## 6. ADR lifecycle

Recommended states:

```text
Proposed
Accepted
Superseded
Rejected
```

Implementation must not present a Proposed ADR as settled fact.

When an ADR is accepted:

- implementation Tasks reference it;
- tests enforce the adopted contract where practical;
- later contradictory changes either amend/supersede the ADR or create a new decision.

## 7. Review checklist

For any compatibility-sensitive PR:

```text
[ ] affected public surface identified
[ ] change classified
[ ] relevant ADR status checked
[ ] consumer evidence reviewed
[ ] compatibility tests updated appropriately
[ ] known defects are not accidentally frozen
[ ] mathematical evidence exists for defect corrections
[ ] migration notes exist for intentional breaks
[ ] human approval obtained for intentional breaks
```

## 8. Default bias

Prefer additive modernization:

- clean modern modules;
- stable legacy facade;
- aliases/adapters where inexpensive;
- corrected shared mathematical implementation underneath both entry points.

Break compatibility only when preserving it would materially damage correctness, safety, or maintainability and the break has been explicitly approved.
