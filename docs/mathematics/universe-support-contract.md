# Universe and Support Contract

- Status: Contract reference for Tasks #9 and #67
- Related ADR: [ADR-0002](../adr/0002-universe-support-semantics.md)
- Current executable surface: `fuzzyroutines.FuzzyRoutines.FuzzySet`

## Canonical vocabulary

| Term               | Meaning                                                            | May be unbounded?               | Exactness rule                                               |
|--------------------|--------------------------------------------------------------------|---------------------------------|--------------------------------------------------------------|
| Universe           | Coordinates on which the membership function defines the fuzzy set | Yes                             | Declared, never inferred from samples                        |
| Integration domain | Finite operational interval used by a continuous numerical method  | No in the initial numerical API | Declared per set or operation                                |
| Positive support   | Coordinates in the universe where membership is strictly positive  | Yes                             | Derived from exact family geometry or explicitly approximate |
| Support closure    | Closure of positive support relative to the universe               | Yes                             | Requires declared topology/interval semantics                |
| Core               | Coordinates with membership exactly one                            | Yes                             | Empty for a non-normal set that never reaches one            |
| Boundary           | Coordinates with membership strictly between zero and one          | Yes                             | Fuzzy transition region, not the topological boundary        |
| Height             | Supremum of membership grades on the universe                      | No; scalar in `[0, 1]`          | Exact where proved, otherwise explicitly approximate         |

The historical `supportSet` name maps only to **integration domain**. It never
asserts positive support or support closure.

## Compatibility examples

| Membership family             | Mathematical result on the real line                     | Example legacy `supportSet` | Interpretation                                |
|-------------------------------|----------------------------------------------------------|-----------------------------|-----------------------------------------------|
| Triangle with feet `0, 2`     | Positive support `(0, 2)`                                | `(-1, 3)`                   | A wider numerical integration window          |
| Increasing shoulder on `0, 1` | Positive support `(0, +infinity)`, core `[1, +infinity)` | `(0, 1)`                    | A finite numerical window, not support        |
| Gaussian centred at `0`       | Positive support is the real line                        | `(-4, 4)`                   | A chosen truncation window for numerical work |

Changing `FuzzySet.supportSet` must change the interval used by legacy
defuzzification without changing the membership evaluator. The compatibility
tests freeze this behavior until the facade delegates to the modern domain
model.

## Representation rule

An analytical membership function and a sampled fuzzy set are different
representations. Scanning a grid may answer a bounded approximate query, but it
cannot establish exact support for a continuous family. Every approximate
derived result must retain the domain, resolution or tolerance, and method that
produced it.

This rule prevents numerical underflow, plotting bounds, or a caller-selected
centroid window from becoming false mathematical metadata.
