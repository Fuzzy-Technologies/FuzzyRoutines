# ADR-0001: Backward-Compatibility Contract for Historical Public API Names

- Status: Accepted on merge
- Date: 2026-09-14
- Related planning task: #8
- Related Feature: #17
- Related compatibility workflow: `docs/architecture/adr-compatibility-workflow.md`

## Context

FuzzyRoutines 1.0.3 exposes a historical, monolithic Python API that is used by
documented examples and known consumers. The modernization roadmap introduces
correctness fixes and focused modules, but a naming cleanup must not become an
unannounced compatibility break.

The legacy API snapshot and consumer inventory are the current evidence base:

- `docs/compatibility/legacy-public-api-1.0.3.md`;
- `docs/compatibility/legacy-consumers.md`;
- `tests/test_legacy_public_api.py`.

## Decision

FuzzyRoutines will preserve the following historical public compatibility
surface unless a later ADR explicitly approves an intentional breaking change:

- module paths `fuzzyroutines` and `fuzzyroutines.FuzzyRoutines`;
- public names `MFunction`, `FuzzySet`, `FuzzyScale`, and
  `UniversalFuzzyScale`;
- public operators `FuzzyNOT`, `FuzzyNOTParabolic`, `FuzzyAND`,
  `FuzzyOR`, `TNorm`, `TNormCompose`, `SCoNorm`, and
  `SCoNormCompose`;
- documented public methods such as `Defuz()`, `Fuzzy()`, and
  `GetLevelByName()`;
- legacy membership-function identifiers and their historical keyword names
  and parameter ordering.

The canonical modernization route is modern-core-first:

1. focused modules own the mathematically correct implementations and the
   default public API for new code;
2. `fuzzyroutines.FuzzyRoutines` remains a compatibility facade for protected
   historical names;
3. historical names delegate to, alias, or explicitly adapt the modern core;
4. compatibility adapters may translate historical parameter names or order,
   but must not duplicate formulas or silently weaken validation;
5. modern names never delegate architecturally to a legacy implementation,
   even when an interim registry maps both names to one bound method.

The compatibility surface is therefore supported but not architecturally
authoritative. New documentation and examples default to the focused modern
API once that API lands. Legacy examples are labelled as compatibility usage.

## Compatibility classification

The following are compatible defect corrections when their historical names and
call shape remain available:

- rejecting mathematically invalid inputs or parameter combinations;
- correcting formula, numerical, logical, or stale-derived-state defects;
- replacing a non-deterministic or unbounded implementation with a mathematically
  equivalent deterministic implementation;
- improving error specificity without changing a valid-result contract.

The following require an explicit intentional-breaking-change decision:

- removing or renaming a protected import path or symbol;
- changing a documented call signature or legacy parameter meaning;
- changing a valid documented return contract for a reason other than correcting
  a demonstrated defect;
- raising the minimum supported Python version beyond the release policy.

Neither an old assertion nor an old example preserves a behavior once it has
been demonstrated to be mathematically invalid. Such a correction must be
documented in the compatibility ledger planned under Feature #31.

## Consequences

- Module extraction and typing work must retain a tested legacy facade.
- Correctness work must state whether a changed observable result is a defect
  correction or an intentional break.
- Legacy import and symbol coverage belongs to Task #96.
- Historical membership conventions are decided separately by ADR-0003.
- Versioning and release classification are decided separately by ADR-0006.

## Acceptance and supersession

This ADR is **Accepted**. Any future decision that narrows this protected
surface must supersede or amend this ADR and include consumer-impact evidence
and an explicit human approval.
