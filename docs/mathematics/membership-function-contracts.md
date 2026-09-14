# Membership-Function Formula and Parameter Contracts

- Status: Contract reference for Task #50
- Related ADR: [ADR-0003](../adr/0003-membership-function-contracts.md)
- Related executable surface: `fuzzyroutines.FuzzyRoutines.MFunction`

## Purpose

This table records the mathematics currently exposed through the historical
factory identifiers. It distinguishes a protected historical identifier from a
standard mathematical name. It does not silently redefine an existing
parameter convention.

A membership function maps an input to a grade in `[0, 1]`, following the
fuzzy-set formulation introduced by [Zadeh (1965)](https://people.eecs.berkeley.edu/~zadeh/papers/Fuzzy%20Sets-Information%20and%20Control-1965.pdf).
All non-degenerate domain constraints below are the target for Task #51; this
document does not implement validation.

## Contract table

| Historical identifier | Canonical mathematical description | Legacy formula and parameter meaning | Non-degenerate domain | Alias policy |
|---|---|---|---|---|
| `hyperbolic` | Rational-power decreasing right shoulder; not a standard hyperbola name | `1` for `x <= c`; otherwise `1 / (1 + (a * (x - c)) ** b)`. `c` is the left cutoff, `a` scale, `b` exponent. | Finite `x, a, b, c`; `a > 0`, `b > 0`. | Keep `hyperbolic`; do not add a false standard-name alias. |
| `bell` | Flat-top piecewise-quadratic bell; not the generalized bell of Jang (1993) | Rising quadratic shoulder from `a` to `b`, plateau from `b` to `c`, then a mirrored falling shoulder ending at `c + b - a`. | Finite `a, b, c`; `a < b <= c`. | Keep `bell`; no `generalizedBell` alias. |
| `parabolic` | Quadratic S-shaped increasing shoulder | Let `t = (x - a) / (b - a)`. It is `0` for `x <= a`, `2t**2` for `0 < t <= 1/2`, `1 - 2(1 - t)**2` for `1/2 < t < 1`, and `1` for `x >= b`. | Finite `a, b`; `a < b`. | Keep `parabolic`; a future modern `sShoulder` alias requires Task #54. |
| `triangle` | Triangular membership function with legacy parameter order | `a` is left foot, **`c` is apex**, `b` is right foot. The geometric order is `a < c < b`, unlike the historical argument order. | Finite `a, b, c`; `a < c < b`. | Preserve `triangle(a, b, c)`; a conventional-order alias must use a different explicit name. |
| `trapezium` | Trapezoidal membership function with legacy parameter order | `a` is left foot, `c` plateau start, `d` plateau end, `b` right foot. The geometric order is `a < c <= d < b`. | Finite `a, b, c, d`; `a < c <= d < b`. | Preserve `trapezium(a, b, c, d)`; a conventional-order alias must use a different explicit name. |
| `exponential` | Gaussian membership function | `exp(-0.5 * ((x - a) / b)**2)`. `a` is the centre and `b` is the scale. | Finite `x, a, b`; canonical scale `b > 0`. The legacy formula is sign-invariant for non-zero `b`. | A `gaussian` alias is permitted only after Tasks #51 and #52 verify this contract. |
| `sigmoidal` | Logistic sigmoid | `1 / (1 + exp(-a * (x - b)))`. `a` is slope and `b` is midpoint. Positive `a` rises; negative `a` falls. | Finite `x, a, b`; `a != 0`. | Keep `sigmoidal`; a future `logistic` alias is semantically exact. |
| `desirability` | Harrington one-sided desirability / Gumbel CDF transform | `exp(-exp(-y))`. It accepts direct input `y` and stores no parameters. | Finite `y`. | Keep `desirability`; `harringtonDesirability` is a semantically exact future alias. |

## Reference naming

The standard parameterized generalized bell used in neuro-fuzzy literature is
not the same formula as the legacy flat-top quadratic `bell` implementation;
see [Jang (1993)](https://doi.org/10.1109/21.256541). The legacy `exponential`
formula is exactly Gaussian-shaped, while legacy `parabolic` is an increasing
quadratic shoulder rather than a Gaussian.

The desirability transform is attributed to E. C. Harrington, *The
Desirability Function*, *Industrial Quality Control* 21(10), 494–498 (1965);
a later peer-reviewed discussion records that provenance
[here](https://ais.khpi.edu.ua/article/view/284553).

## Compatibility rule

Historical factory identifiers, keyword names, and parameter ordering remain
part of the public compatibility surface. Invalid or degenerate configurations
are not compatibility requirements: Task #51 must reject them explicitly
rather than returning a plausible membership grade of zero.
